# sources/user-network-fs/samba/source4/ntvfs/posix/vfs_posix.c

Purpose: `vfs_posix.c` is the entry point and tree-connect setup for Samba4's POSIX NTVFS disk backend. It registers the backend as both `default` and `posix`, constructs per-share `pvfs_state`, initializes locking/notify/search helpers, and wires the NTVFS operation table to the POSIX implementation files.

Important APIs, types, and functions: Key functions are `pvfs_setup_options`, `pvfs_state_destructor`, `pvfs_connect`, `pvfs_disconnect`, `pvfs_chkpath`, `pvfs_copy`, `pvfs_lpq`, `pvfs_trans`, and `ntvfs_posix_init`. The operation table references many integration functions such as `pvfs_open`, `pvfs_read`, `pvfs_write`, `pvfs_lock`, `pvfs_notify`, and `pvfs_async_setup`.

Control flow: On connect, the module normalizes the share name, initializes ACL backends, allocates `pvfs_state`, trims the share path, verifies it is an existing directory, sets reported filesystem/device strings, creates byte-range locking and open database contexts, initializes change notify and search id tracking, initializes name mangling, reads share options, installs a destructor, and blocks `SIGXFSZ` when available. Registration fills `struct ntvfs_ops` and calls `ntvfs_register`.

State and persistence behavior: Per-tree state includes base directory, flags, share name, TDB-backed EADB handle, open file list, open search id tree, oplock/write-delay settings, locking contexts, notify context, SID cache, and ACL backend. Durable state lives in underlying files, optional external EADB, open database, brlock database, and xattrs.

Dependencies and integration points: It depends on `share_config` options, loadparm TDB flags, tdb-wrap, idtree, ntvfs common code, brlock, opendb, notify, ACL modules, and the rest of the `pvfs_*` implementation files.

Risks: Share options directly change security and compatibility behavior, especially xattrs, permission override, case sensitivity, ACL backend selection, fake oplocks, and read-only handling. A failed EADB open disables xattr support. The backend reports NTFS-like capabilities over POSIX filesystems, so metadata emulation must stay consistent across files.

Test signals: Integration tests should tree-connect to POSIX-backed shares under varied share options, verify xattr/EADB fallback, read-only rejection, path checking, locking/notify behavior, ACL backend selection, and registration under both `default` and `posix`.
