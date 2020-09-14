kind: import
description: sample element for testing assert_license

runtime-depends:
  - build_dep_runtime_dep.bst
build-depends:
  - build_dep_build_dep.bst

public:
  licenses:
    license-strings:
    - BD license 1
    - BD license (2.0)

sources:
- kind: local
  path: files/File-A.txt
