# File Research: sources/virtualization/guestfs-tools/cat/test-docs.sh

## Scope

Documentation consistency test for `virt-cat`.

## Behavior

- Sources common test functions and honors skip configuration.
- Runs `podcheck.pl` against `virt-cat.pod` with the common options path.

## Dependencies And Risks

- Verifies docs/options consistency only.
