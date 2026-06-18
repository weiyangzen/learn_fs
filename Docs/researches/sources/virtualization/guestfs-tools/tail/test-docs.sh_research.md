# File Research: sources/virtualization/guestfs-tools/tail/test-docs.sh

Documentation/CLI consistency test for `virt-tail`.

Key behavior:
- Sources shared test functions and honors skip environment.
- Runs `podcheck.pl` against `virt-tail.pod` and command `virt-tail`.
- Supplies common options path.

Research notes:
- This is a docs/help validation test only.
