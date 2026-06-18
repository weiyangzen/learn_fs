# File Research: sources/virtualization/libguestfs/daemon/grub.c

Wraps legacy `grub-install`.

Important behavior:
- `optgroup_grub_available` checks for `grub-install`.
- `do_grub_install(root, device)` constructs `--root-directory=<sysroot><root>`.
- Captures stderr and, in verbose mode, stdout.

Filesystem relevance: installs a bootloader into a guest-mounted root and target block device.
