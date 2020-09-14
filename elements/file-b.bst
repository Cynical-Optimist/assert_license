kind: import
description: sample element for testing assert_license

build-depends:
  - build_dep.bst

public:
  licenses:
    license-strings:
    - bar license 1
    - bar license (2.0)
    - bar-bar license

sources:
- kind: local
  path: files/File-A.txt
