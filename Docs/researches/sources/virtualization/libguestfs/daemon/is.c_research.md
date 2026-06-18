# File Research: sources/virtualization/libguestfs/daemon/is.c

Implements simple existence and file-type predicates.

Important behavior:
- Shared `get_mode(path, mode, followsymlinks)` uses `lstat` or `stat` under chroot.
- `ENOENT` and `ENOTDIR` return false, not error.
- Exposes `exists`, `is_chardev`, `is_blockdev`, `is_fifo`, and `is_socket`.
- Optional `followsymlinks` defaults to false unless corresponding optarg bit is set.

Filesystem relevance: guest path metadata classification.
