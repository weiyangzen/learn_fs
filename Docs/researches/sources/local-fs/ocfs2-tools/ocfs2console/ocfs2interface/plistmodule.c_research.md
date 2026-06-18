# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/plistmodule.c

Python 2 C extension wrapping `ocfs_partition_list` as module `plist`.

Exposed function:
- `partition_list(callback, data=None, filter=None, fstype=None, unmounted=False, async=False)`

Callback argument behavior:
- Always passes `device`.
- Passes `mountpoint` only when `unmounted` is false.
- Always passes `fstype`.
- Passes `data` if provided.

Implementation:
- `ProxyData` stores Python callback/data and flags.
- `proxy()` converts `OcfsPartitionInfo` into Python tuple and calls callback.
- Stops invoking callback after first Python error, printing the error.
- Module init registers `partition_list`.

Dependencies:
- GLib
- `ocfsplist.h`

Notable details:
- Python callback exceptions are printed and suppress further proxy calls, but `partition_list` still returns `None`.
- Python 2 C API only.
