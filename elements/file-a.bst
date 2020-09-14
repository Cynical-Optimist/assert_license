kind: import
description: sample element for testing assert_license

runtime-depends:
  - runtime_dep.bst

public:
  licenses:
    license-strings:
    - foo license 1
    - foo license (2.0)
    - foo-foo license

sources:
- kind: local
  path: files/File-A.txt
