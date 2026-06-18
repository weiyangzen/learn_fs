# File Research: sources/virtualization/guestfs-tools/check-mli.sh

## Scope

Repository consistency test requiring OCaml implementation files to have matching interfaces.

## Behavior

- Finds `*.ml` files, excluding builder templates, contrib, OCaml examples/tests, bindtests, and `_tests.ml`.
- For each remaining `.ml`, checks for a sibling `.mli`.
- Reports missing interface files and exits nonzero if any are missing.

## Dependencies And Risks

- The rule exists because Makefile dependency generation is difficult without `.mli` files.
- Exclusion list must track intentional implementation-only OCaml files.
