# File Research: sources/virtualization/guestfs-tools/diff/test-virt-diff-docs.sh

## Scope

Documentation consistency test for `virt-diff`.

## Behavior

- Runs `podcheck.pl` against `virt-diff.pod`.
- Supplies common options path.
- Ignores documented aliases/options that map to internal canonical options.

## Dependencies And Risks

- Covers docs/options consistency only.
