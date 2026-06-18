# File Research: sources/virtualization/libguestfs/daemon/fstrim.c

Implements discard/TRIM support.

Important behavior:
- `optgroup_fstrim_available` checks for `fstrim`.
- `do_fstrim` validates optional `offset >= 0`, `length > 0`, and `minimumfreeextent > 0`.
- Converts the guest path to `sysroot_path`.
- Calls `sync_disks()` before and after trimming.
- Runs `fstrim` twice as a documented workaround for RHEL-88450.
- Maps “discard operation is not supported” errors to `ENOTSUP`.

Filesystem relevance: bridges mounted filesystem discard support to the backing virtual block device.
