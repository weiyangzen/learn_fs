# sources/user-network-fs/samba/source3/libsmb/libsmb_cache.c

Purpose: implements the default in-process libsmbclient server cache used when applications do not provide external cache callbacks. It stores `SMBCSRV *` connections by server, share, workgroup, and username so repeated URL operations can reuse SMB sessions/tree connects.

Important APIs/types: private `struct smbc_server_cache` holds duplicated key strings, an `SMBCSRV *server`, and DLIST links. `SMBC_add_cached_server()` allocates and links a cache record. `SMBC_get_cached_server()` searches by server/workgroup/user and share semantics. `SMBC_remove_cached_server()` unlinks and frees only the cache node, not the `SMBCSRV`. `SMBC_purge_cached_servers()` iterates cache entries and asks `SMBC_remove_unused_server()` to close unused servers.

Control flow and state: cache records live at `context->internal->server_cache`. Lookup treats exact share matches as strongest. Empty share and `*IPC$` are special attribute/browse connections and are never returned for a non-exact data-share request. If `one_share_per_server` is enabled and an existing data share differs, the code issues `cli_tdis()`, updates the cached share name, and returns the same connection for a later tree connect.

Dependencies and integration: relies on Samba allocation macros, `DLIST_ADD/REMOVE`, `cli_tdis()`, `cli_shutdown()`, and context option/callback accessors. It is wired as the default cache implementation by `smbc_new_context()` and consumed by `SMBC_find_server()` / `SMBC_server()`.

Risks: cache identity excludes password and port; callers rely on workgroup/user/share/server partitioning and surrounding connection setup to avoid credential mixups. One-share-per-server mutates cache state and can drop broken connections on failed disconnect or strdup. Tests should exercise exact share reuse, `*IPC$` isolation, one-share-per-server retargeting, purge refusal while files are open, and ENOMEM cleanup paths.
