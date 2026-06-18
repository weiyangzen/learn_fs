# File Research: sources/os/linux/linux-stable/fs/cachefiles/xattr.c

This file manages CacheFiles coherency metadata stored as user xattrs on backing files and volume directories.

Object xattr:
- Name: `user.CacheFiles.cache`.
- `struct cachefiles_xattr` stores:
  - big-endian object size
  - zero point
  - object type
  - content state
  - netfs auxiliary coherency data.
- `cachefiles_set_object_xattr()` writes object size, content state, and auxdata. Local-write cookies are marked `CACHEFILES_CONTENT_DIRTY`.
- `cachefiles_check_auxdata()` reads and validates the object xattr against expected type, auxdata, object size, and dirty state. Dirty objects are currently treated stale with a warning and TODO for conflict resolution.
- `cachefiles_remove_object_xattr()` removes the xattr to mark an object stale, treating missing xattr as success.

Write marker:
- `cachefiles_prepare_to_write()` writes an object xattr before local write unless the object is currently an unlinked tmpfile.

Volume xattr:
- `struct cachefiles_vol_xattr` stores reserved zero field plus FS-Cache volume coherency data.
- `cachefiles_set_volume_xattr()` writes volume coherency data.
- `cachefiles_check_volume_xattr()` validates xattr length, reserved field, and coherency bytes.

Operational details:
- Xattr writes use `mnt_want_write_file()` or `mnt_want_write()` around VFS set/remove operations.
- Error injection hooks can force read/write/remove failures.
- Non-memory VFS failures generally mark the cache or object as I/O failed.
- Tracepoints record coherency success/failure reason for object and volume checks.
