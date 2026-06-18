# File Research: sources/virtualization/guestfs-tools/customize/test-virt-customize-docs.sh

## Scope

Documentation consistency test for `virt-customize`.

## Behavior

- Runs `podcheck.pl` on `virt-customize.pod`.
- Supplies common options path and inserts common customize synopsis/options POD fragments.
- Ignores `--dryrun`.

## Dependencies And Risks

- Documentation must remain aligned with generated/common option fragments.
