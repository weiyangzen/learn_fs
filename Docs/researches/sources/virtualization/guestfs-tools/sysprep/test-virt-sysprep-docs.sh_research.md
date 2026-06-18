# File Research: sources/virtualization/guestfs-tools/sysprep/test-virt-sysprep-docs.sh

Documentation/CLI consistency test for `virt-sysprep`.

Key behavior:
- Runs `podcheck.pl` against `virt-sysprep.pod` and command `virt-sysprep`.
- Supplies common options path and inserts generated `sysprep-extra-options.pod` and `sysprep-operations.pod`.
- Ignores `--dryrun`, `--dump-pod`, and `--dump-pod-options`.

Research notes:
- This test depends on generated POD snippets produced by the `Makefile.am` documentation rules.
