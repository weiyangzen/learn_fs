# File Research: sources/virtualization/libguestfs/daemon/available.c

Implements feature and filesystem availability queries.

Key points:
- `do_internal_feature_available` searches generated `optgroups[]` and returns `0` available, `1` unavailable, `2` unknown group.
- `do_available_all_groups` returns all optional group names.
- `filesystem_available` checks `/proc/filesystems` through `grep`, then optionally tries `modprobe` if Linux module support is available.
- `do_filesystem_available` validates filesystem names as alnum or underscore before probing.
- Designed so the internal probe path avoids `reply_with_error`, allowing callers to control error reporting.
