# sources/user-network-fs/samba/source4/ntvfs/posix/python/pyxattr_tdb.c

Purpose: `pyxattr_tdb.c` implements the `samba.xattr_tdb` Python extension, providing xattr-like access backed by Samba's TDB/dbwrap storage instead of native filesystem xattrs. It supports filesystems without suitable xattr support and aligns with source3 `xattr_tdb`.

Important APIs, types, and functions: The exported Python methods are `wrap_setxattr(tdbname, filename, attribute, value)`, `wrap_getxattr(tdbname, filename, attribute)`, and `is_xattr_supported()`. The implementation uses `py_default_loadparm_context`, `db_open_tdb`, `xattr_tdb_setattr`, `xattr_tdb_getattr`, `struct file_id`, and `stat`.

Control flow: Each get or set opens the named TDB with Samba loadparm-derived TDB flags, stats the target file, builds a `file_id` from device and inode, and stores or retrieves the attribute value from the database. Errors are converted into Python exceptions before the temporary talloc context is freed.

State and persistence behavior: Attribute data persists in the external TDB keyed by the file's device and inode. No module-level handle is cached; every call opens the database anew. File renames preserve lookup identity through inode/device, while replacement creates a new identity.

Dependencies and integration points: It depends on Samba dbwrap, tdb, `xattr_tdb`, Python/talloc bridge code, and the `pyparam_util` loadparm helper. The POSIX build file installs it as `samba/xattr_tdb.so`.

Risks: Per-call database open cost and lock ordering matter for callers doing many xattr operations. Device/inode identity can become stale if files are deleted and inodes reused. Several failures are reported as generic `IOError` or `TypeError`, which can obscure storage corruption versus missing attributes.

Test signals: Tests should cover binary round trips, missing files, missing attributes, persistence across process/module reloads, replacement of a file at the same path, and interaction with Samba TDB lock flags.
