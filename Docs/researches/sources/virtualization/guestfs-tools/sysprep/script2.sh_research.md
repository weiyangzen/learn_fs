# File Research: sources/virtualization/guestfs-tools/sysprep/script2.sh

Helper script for `test-virt-sysprep-script.sh`.

Key behavior:
- Removes `etc/resolv.conf` relative to the temporary script execution directory.
- Writes its current working directory to `$abs_builddir/stamp-script2.sh`.
- Used with `script1.sh` to verify multiple scripts run.
