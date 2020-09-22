#
#  Copyright 2020 Codethink Limited
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#  Authors:
#        Douglas Winship <douglas.winship@codethink.co.uk>

"""
assert_license - read licenses from dependency public data
==========================================================
"""

import json
import os.path
from buildstream import Element, ElementError, Scope


def license_matches(blacklist_entry, license_string):
    "Test whether a given line of license info violates a given line from the blacklist"
    # This is a provisional version of the function, and will be updated soon.
    # For now, a 'match' is true if either line contains the other line.
    # But other options should be considered (such as regEx matching)

    # Also: the function should be expanded to handle license strings containing
    # "OR" and "AND" statements.

    if blacklist_entry in license_string:
        return True
    if license_string in blacklist_entry:
        return True
    return False


class AssertLicenseElement(Element):
    def configure(self, node):
        self.node_validate(node, ["path", "blacklist", "dependency_scope"])
        self.path = self.node_subst_member(node, "path")
        self.blacklist = self.node_subst_list(node, "blacklist")

        dependency_scope = self.node_subst_member(node, "dependency_scope").lower()
        if dependency_scope == "run":
            self.dep_scope = Scope.RUN
        elif dependency_scope == "build":
            self.dep_scope = Scope.BUILD
        elif dependency_scope == "all":
            self.dep_scope = Scope.ALL
        elif dependency_scope == "none":
            self.dep_scope = None
        else:
            raise ElementError(
                f"Incorrect value supplied for depstype: {dependency_scope}"
                "\nAcceptable values: run, build, all"
            )

    def preflight(self):
        pass

    def get_unique_key(self):
        # At time of writing, I'm not sure what (if anything) to use as a unique key
        return {
            "scope": str(self.dep_scope),
            "path": self.path,
            "blacklist": self.blacklist,
        }

    def configure_sandbox(self, sandbox):
        pass

    def stage(self, sandbox):
        pass

    def get_deps(self):
        already_visited = []
        for build_dep in self.dependencies(Scope.BUILD, recurse=False):
            # The direct build dependencies should always be included
            if build_dep not in already_visited:
                already_visited.append(build_dep)
                yield build_dep
            # If scope isn't 'None'
            if self.dep_scope:
                for dep in build_dep.dependencies(self.dep_scope):
                    if dep not in already_visited:
                        already_visited.append(dep)
                        yield dep

    def assemble(self, sandbox):
        output_dict = {}
        blacklist_violations = False
        for dep in self.get_deps():
            license_strings = dep.get_public_data("licenses")["license-strings"]
            output_dict[dep.name] = license_strings
            for blacklist_string in self.blacklist:
                for license_string in license_strings:
                    if license_matches(blacklist_string, license_string):
                        self.warn(
                            "Blacklist violation",
                            detail=(
                                f"In Element: {dep.name},"
                                f' license string "{license_string}" conflicts with'
                                f' blacklist entry "{blacklist_string}"'
                            ),
                        )
                        blacklist_violations = True

        if blacklist_violations:
            raise ElementError("assert_license element detected a blacklist violation")

        basedir = sandbox.get_directory()
        path = os.path.join(basedir, self.path)
        with open(path, mode="w") as outfile:
            json.dump(output_dict, outfile, indent=2)
            outfile.write("\n")

        return os.path.sep


def setup():
    return AssertLicenseElement
