# File Research: sources/virtualization/guestfs-tools/df/test-virt-df-docs.sh

## Scope

Documentation consistency test for `virt-df`.

## Behavior

- Runs `podcheck.pl` against `virt-df.pod` with common options path after honoring skips.

## Dependencies And Risks

- Checks documentation/options consistency only.
