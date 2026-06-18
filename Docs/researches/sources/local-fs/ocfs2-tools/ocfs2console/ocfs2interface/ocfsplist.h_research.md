# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/ocfsplist.h

Header for the OCFS partition-list helper.

Key types:
- `OcfsPartitionInfo`
  - `device`
  - `mountpoint`
  - `fstype`
- `OcfsPartitionListFunc`
  - Callback taking `OcfsPartitionInfo *` and user data.

Key declaration:
- `ocfs_partition_list(func, data, filter, fstype, unmounted, async)`

Dependencies:
- GLib types.

Usage:
- Implemented by `ocfsplist.c`.
- Wrapped for Python by `plistmodule.c`.
