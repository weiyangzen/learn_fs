# File Research: sources/virtualization/guestfs-tools/sysprep/script1.sh

Helper script for `test-virt-sysprep-script.sh`.

Key behavior:
- Writes its current working directory to `$abs_builddir/stamp-script1.sh`.
- Used to prove a `virt-sysprep --script` hook executed successfully.
