# File Research: sources/virtualization/guestfs-tools/drivers/test-virt-drivers-docs.sh

## Scope

Documentation consistency test for `virt-drivers`.

## Behavior

- Runs `podcheck.pl` on `virt-drivers.pod` with the common options path after honoring skips.

## Dependencies And Risks

- Checks docs/options consistency only.
