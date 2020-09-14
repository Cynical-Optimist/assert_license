kind: import
description: sample element for testing assert_license

runtime-depends:
- runtime_dep_runtime_dep.bst
build-depends:
- runtime_dep_build_dep.bst

public:
  licenses:
    license-strings:
    - RD license 1
    - RD license (2.0)

sources:
- kind: local
  path: files/File-A.txt
