# File Research: sources/virtualization/guestfs-tools/sysprep/test-virt-sysprep-backup-files.sh

Test for the `virt-sysprep` `backup-files` operation.

Key behavior:
- Requires the phony Fedora guest image.
- Creates a qcow2 overlay backed by `fedora.img`.
- Adds backup-like files in `/bin`, `/usr/share`, `/etc/fstab.bak`, and `/etc/resolv.conf~`.
- Captures a `find /` listing inside the guest before sysprep.
- Runs `virt-sysprep --enable backup-files`.
- Captures the file listing after and diffs it against the original.

Research notes:
- The comments say `/bin` and `/usr` are not on the whitelist and should not be deleted; the test also effectively checks the final file tree is unchanged for this setup.
