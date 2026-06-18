# sources/user-network-fs/samba/source3/libsmb/libsmb_stat.c

Purpose: implements `stat`, `fstat`, `statvfs`, and `fstatvfs` behavior for libsmbclient, translating SMB file attributes and filesystem information into POSIX-like structures.

Important APIs: `setup_stat()` maps SMB attributes, size, inode, dev, and timestamps into `struct stat`, using execute bits as archive/system/hidden markers and write bit for non-readonly. `SMBC_stat_ctx()` parses a URL, connects, and calls `SMBC_getatr()`. `SMBC_fstat_ctx()` validates an open handle, resolves the stored URL through DFS, calls `cli_qfileinfo_basic()`, and fills stat. `SMBC_statvfs_ctx()` opens the path as directory or file and delegates to `SMBC_fstatvfs_ctx()`. `SMBC_fstatvfs_ctx()` fills block/free-node fields from Unix CIFS or full-size info and sets feature flags.

Control flow/state: no independent persistent state is added. It consumes server dev ids, current file handles, and context options. Inode fallback uses `str_checksum(name)` when the server does not provide one.

Dependencies and integration: depends on `SMBC_parse_path`, `SMBC_server`, `SMBC_getatr`, file/dir open/close implementations, DFS `cli_resolve_path`, `smbXcli` tcon helpers, and time helpers. It is called directly by compatibility wrappers and indirectly by statvfs path probing.

Risks: POSIX mode mapping is an approximation, not ACL-aware. Generated inode values can collide or change with path spelling. `SMBC_statvfs_ctx()` has open/close side effects and can fail if opening a readable path is not permitted. Tests should cover directory/file mode mapping, readonly and archive/system/hidden bits, server-provided vs generated inode, fstat on directories delegating to fstatdir, Unix CIFS vs non-Unix filesystem info, DFS flag, case-insensitive flag, and close cleanup after statvfs.
