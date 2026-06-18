# File Research: sources/virtualization/guestfs-tools/builder/test-config/virt-builder/repos.d/test-index.conf.in

## Scope

Test repository configuration template for native virt-builder index tests.

## Contents

- Defines `[test-index]`.
- Points `uri` to `file://@abs_top_builddir@/builder/test-index`.

## Risks And Invariants

- Configure substitutes the absolute build directory.
- The referenced `test-index` file must exist in the builder build directory for list/build tests.
