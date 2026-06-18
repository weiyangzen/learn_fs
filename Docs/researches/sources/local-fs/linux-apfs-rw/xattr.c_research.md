# File Research: sources/local-fs/linux-apfs-rw/xattr.c

This file implements APFS extended attribute support for the Linux VFS xattr interface and for APFS-internal compressed-resource data. APFS stores xattr records in the catalog tree, with values either embedded inline or referenced through a separate data stream.

Public/internal APIs:
- `____apfs_xattr_get()` reads a named xattr, optionally allowing partial reads for header-only compressed-file probing.
- `__apfs_xattr_get()` wraps the strict whole-value read form without locking.
- `apfs_xattr_get_compressed_data()` loads compressed data metadata/value for compression paths.
- `apfs_release_compressed_data()` releases storage allocated by compressed-data lookup.
- `apfs_compressed_data_read()` reads from inline compressed data or dstream-backed compressed data.
- `apfs_xattr_set()` creates, replaces, or deletes a named APFS xattr inside an active transaction.
- `apfs_delete_all_xattrs()` removes all xattrs for an inode while the caller holds `nx_big_sem` for writing.
- `apfs_listxattr()` implements VFS listxattr with the fake Linux namespace prefix.

Core control flow:
- `apfs_xattr_from_query()` converts a successful catalog-tree query into an in-memory `struct apfs_xattr`, validating name length, NUL termination, value length, and dstream flag consistency.
- Inline reads copy directly from catalog record value bytes.
- Dstream reads allocate a temporary `apfs_dstream_info`, populate it from xattr metadata, and call `apfs_nonsparse_dstream_read()`.
- Set operations build a catalog key/value pair, choose inline versus dstream storage based on `APFS_XATTR_MAX_EMBEDDED_SIZE`, insert or replace the btree record, then truncate any old dstream after the record has been replaced.
- Delete operations remove inline xattrs directly; dstream xattrs remove the catalog record first and then truncate the associated dstream.
- VFS `.get` and `.set` handlers intentionally strip the fake `XATTR_MAC_OSX_PREFIX`; on disk APFS xattrs have no Linux namespace prefix.

Kernel compatibility:
- `apfs_xattr_osx_set()` has signature variants for kernels before 5.12, kernels before 6.3 excluding newer RHEL 9.6 handling, and newer kernels using `struct mnt_idmap`.

Integration points:
- `apfs_xattr_handlers` is used by the inode operations.
- `apfs_listxattr()` is wired in `namei.c`, `file.c`, and `symlink.c`.
- Compression code calls `____apfs_xattr_get()` and `apfs_xattr_get_compressed_data()`.
- Symlink creation uses `apfs_xattr_set()` for `APFS_XATTR_NAME_SYMLINK`.

Error handling and safety:
- Corrupt on-disk records return `-EFSCORRUPTED` after consistency checks.
- Oversized dstream-backed xattrs return `-E2BIG` if the 64-bit APFS size cannot fit Linux `int` handling.
- VFS whole-read semantics return `-ERANGE` if the user buffer is too small.
- Allocation failures return `-ENOMEM`; btree and transaction failures propagate.
- `apfs_xattr_get()` serializes reads with `nx_big_sem`; transaction-starting VFS set wraps `apfs_xattr_set()` with commit/abort.

Risks and watchpoints:
- Dstream creation writes blocks before the catalog xattr record exists; failure cleanup frees the temporary dstream object but relies on transaction semantics for on-disk rollback.
- `apfs_create_xattr_dstream()` uses pointer arithmetic on `const void *value`, which is accepted as a compiler extension but is not strictly standard C.
- Several size paths narrow APFS 64-bit sizes to `int`; the file has an explicit TODO for huge compressed files.
