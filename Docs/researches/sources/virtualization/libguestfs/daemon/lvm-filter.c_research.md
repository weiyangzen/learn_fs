# File Research: sources/virtualization/libguestfs/daemon/lvm-filter.c

Manages the daemon’s LVM device filter configuration.

Important behavior:
- Reads `LVM_SYSTEM_DIR` at constructor time, defaulting to `/etc/lvm`.
- Rewrites `lvm.conf` with `filter` and `global_filter`.
- Disables LVM devices-file use when supported by `lvmdevices`/`vgimportdevices`.
- `do_lvm_set_filter` builds allow regexes for exact devices and whole-disk partitions, then rejects everything else.
- Filter changes deactivate VGs, write config, clear cache/rescan, then reactivate.
- `do_lvm_clear_filter` restores allow-all filtering.

Filesystem relevance: constrains LVM discovery to intended block devices, reducing cross-disk contamination in appliance operations.
