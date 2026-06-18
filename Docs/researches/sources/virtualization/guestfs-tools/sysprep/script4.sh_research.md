# File Research: sources/virtualization/guestfs-tools/sysprep/script4.sh

Temporary-directory isolation helper for `test-virt-sysprep-script.sh`.

Key behavior:
- Appends current working directory to `$abs_builddir/stamp-script4.sh`.
- Used twice to verify separate `virt-sysprep --script` runs use distinct temporary directories.
