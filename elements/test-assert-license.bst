kind: assert_license

build-depends:
- file-a.bst
- file-b.bst

config:
  dependency_scope: all
  path: assert_license_output.txt
  blacklist:
    - foo license
    - RD license (3.0)
    - Foo_Bar_Baz_Qux
