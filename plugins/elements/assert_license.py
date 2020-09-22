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



class AssertLicenseElement(Element):
    def configure(self, node):
        self.node_validate(node, ["dependency_scope", "path"])
        self.path = self.node_subst_member(node, "path")

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
        }

    def configure_sandbox(self, sandbox):
        pass

    def stage(self, sandbox):
        pass

    def assemble(self, sandbox):
        output_dict = {}
        for dep in self.get_deps():
            output_dict[dep.name] = dep.get_public_data("licenses")["license-strings"]

        basedir = sandbox.get_directory()
        path = os.path.join(basedir, self.path)
        with open(path, mode="w") as outfile:
            json.dump(output_dict, outfile, indent=2)
            outfile.write("\n")

        return os.path.sep

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


def setup():
    return AssertLicenseElement
