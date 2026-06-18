# File Research: sources/os/linux/linux/fs/xfs/scrub/xfblob.h

This header declares the xfile-backed variable-length blob store API used by scrub/repair scratch structures.

Key types:
- `struct xfblob`: owns backing `xfile` and the next append offset.
- `xfblob_cookie`: `loff_t` offset cookie identifying a stored blob.

Declared functions:
- Lifecycle: `xfblob_create`, `xfblob_destroy`.
- Blob operations: `xfblob_store`, `xfblob_load`, `xfblob_free`.
- Utility: `xfblob_bytes`, `xfblob_truncate`.

Name helpers:
- `xfblob_storename`: stores an `xfs_name` byte string.
- `xfblob_loadname`: loads bytes into an `xfs_name` and sets `xname->len`.

Risk notes:
- `xfblob_loadname` casts `xname->name` to mutable storage, so callers must provide an `xfs_name` whose name buffer is writable and large enough.
- Size checking is enforced by `xfblob_load`; callers must track expected blob size separately.
