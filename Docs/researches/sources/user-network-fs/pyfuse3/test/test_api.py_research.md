# sources/user-network-fs/pyfuse3/test/test_api.py

Purpose: Unit tests for selected pyfuse3 public APIs that do not require mounting a FUSE filesystem.

Important APIs/types/functions: Tests `pyfuse3.listdir`, `get_sup_groups`, `syncfs`, xattr helpers, `EntryAttributes`, `SetattrFields`, `RequestContext`, `StatvfsData`, and `FUSEError` copy/pickle behavior. `_getxattr_helper` compares pyfuse3 xattr access with Python `os.getxattr`.

Control flow: Each test calls pyfuse3 APIs directly. `test_xattr` creates a temporary file, verifies missing xattrs, sets via pyfuse3, optionally sets via `os`, and compares values. `test_copy` confirms unpickleable native request structs and copyable attribute/stat structs.

State and persistence: Uses temporary files and host `/usr/bin` listing. No persistent project state.

Dependencies and integration points: Depends on a built pyfuse3 extension and host OS APIs for groups, syncfs, xattrs, and directory listings.

Risks: `/usr/bin` can change during `test_listdir`. Xattr support depends on filesystem mount options and may skip on `ENOTSUP`. Host group state and permissions affect tests.

Test signals: Provides smoke coverage for native extension wrappers, timestamp precision storage, xattr portability, and object copy semantics.
