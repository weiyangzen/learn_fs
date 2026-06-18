<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/btrfs.c -->
## sources/test-tools/strace/src/btrfs.c

Purpose: Implements the mpers-aware Btrfs ioctl decoder, covering Btrfs administrative, device, balance, quota, scrub, search, send, space, and subvolume operations.

Important APIs and types: Exports `MPERS_PRINTER_DECL(int, btrfs_ioctl, ...)`. Helper printers cover balance args, feature flags, qgroup limits/inheritance, data containers, search keys and headers, space info, timespecs, scrub progress, and device replacement start/status parameters. It uses mpers aliases for several Btrfs structs that contain pointers or layout-sensitive fields.

Control flow: `btrfs_ioctl` switches on ioctl code. No-argument commands return decoded immediately. Scalar commands print integer or flag arguments. Read-only commands commonly return `0` on entry and decode on exit. Read/write commands print input on entry, then use `tprint_value_changed()` on successful exit to print output fields. Complex branches decode balance state, defrag ranges, device info/replacement, feature arrays, fs info, device stats arrays, inode lookup/path containers, logical inode containers, quota commands/status, received subvolume timestamps, scrub progress, tree-search buffers, send clone source arrays, space info arrays, and vol args for snapshot/device operations.

State and persistence: Uses `set_tcb_priv_ulong` to remember whether `BTRFS_IOC_INO_LOOKUP` used implicit root tree id. Otherwise state is transient and fetched from tracee memory. Output behavior depends on entry/exit phase and `syserror(tcp)`.

Dependencies and integration: Depends on `defs.h`, `linux/btrfs_tree.h`, `linux/fs.h`, mpers definitions, and many Btrfs xlat tables. Integrated through the generic ioctl dispatcher, returning `RVAL_IOCTL_DECODED` for recognized commands.

Risks: Btrfs ioctl structs are large and version-sensitive; mpers pointer fields and kernel layout drift are high-risk. Array/container printing must respect abbreviation and sequence truncation. Search buffer decoding guards offset overflow but still depends on correct kernel-provided lengths.

Test signals: Btrfs tests should cover entry/exit behavior for read/write ioctls, failed syscalls, short and long arrays, tree-search v1/v2 including `EOVERFLOW`, quota inheritance, scrub/device replacement statuses, feature arrays, and compat personalities.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/btrfs.c -->
