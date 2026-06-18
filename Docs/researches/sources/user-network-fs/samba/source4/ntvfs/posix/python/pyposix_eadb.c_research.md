# sources/user-network-fs/samba/source4/ntvfs/posix/python/pyposix_eadb.c

Purpose: `pyposix_eadb.c` exposes a small Python module, `posix_eadb`, for manipulating PVFS TDB-backed extended attributes from Python tests or tooling.

Important APIs, types, and functions: The module exports `wrap_getxattr`, `wrap_setxattr`, and `is_xattr_supported`. Local functions are `py_is_xattr_supported`, `py_wrap_setxattr`, `py_wrap_getxattr`, and `MODULE_INIT_FUNC(posix_eadb)`. It uses `DATA_BLOB`, `struct tdb_wrap`, Python bytes parsing/building macros, `PyErr_SetNTSTATUS`, and `py_default_loadparm_context`.

Control flow: `is_xattr_supported` always returns true for this wrapper. `wrap_setxattr` parses TDB path, filename, attribute name, and bytes payload; opens or creates the TDB with loadparm-derived flags; calls `push_xattr_blob_tdb_raw`; maps open failures to `IOError` and NTSTATUS failures to Python exceptions; then returns `None`. `wrap_getxattr` parses TDB path, filename, and attribute name; opens or creates the TDB; calls `pull_xattr_blob_tdb_raw` with an estimated size; builds a Python bytes object from the returned blob; and frees the talloc context.

State and persistence behavior: Attribute data is persisted in the named TDB file using raw posix_eadb helpers. Each operation creates a temporary talloc context and opens the TDB independently. There is no module-global cache.

Dependencies and integration points: It depends on Samba Python compatibility headers, TDB wrap, NDR/data blob utilities, posix_eadb raw helpers, loadparm Python context, and Python NTSTATUS error helpers. It likely supports tests that need to inspect or seed the EADB backend without mounting through SMB.

Risks: The function docstrings omit the TDB-name argument even though parsing requires it. The module reports xattr support unconditionally because it targets EADB, not the host filesystem xattr API. The get wrapper uses a fixed estimated size of 100, relying on the backend to grow if needed.

Test signals: Cover set/get round trips with binary bytes, missing attribute errors, TDB open failure, NTSTATUS-to-Python exception mapping, repeated opens, and argument validation under Python 3 bytes handling.
