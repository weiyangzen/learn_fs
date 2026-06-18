# File Research: sources/virtualization/libguestfs/daemon/clevis-luks.c

Wraps Clevis LUKS unlock support.

Key points:
- Optional group availability checks for `clevis-luks-unlock`.
- `do_clevis_luks_unlock` executes `clevis luks unlock -d <device> -n <mapname>`.
- Errors include both device and mapper name.
- Calls `udev_settle()` after successful unlock so new mapper nodes are ready.
