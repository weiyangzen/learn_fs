# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/xfblob.h

Declares the xfile-backed blob storage API.

Key elements:
- `struct xfblob` stores the backing xfile and next append offset.
- `xfblob_cookie` is a `loff_t` offset cookie.
- Public operations cover create/destroy, load, store, free, bytes used, and truncate.
- `xfblob_storename` stores an `xfs_name` byte string as a blob.
- `xfblob_loadname` loads a blob into an `xfs_name` buffer and sets the name length to the caller-supplied size.

Important detail:
- Name helpers are thin wrappers and rely on the caller-provided size/capacity being correct.
