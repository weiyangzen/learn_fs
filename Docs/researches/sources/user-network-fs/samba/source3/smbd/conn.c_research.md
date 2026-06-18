# sources/user-network-fs/samba/source3/smbd/conn.c

## Purpose
`conn.c` allocates, initializes, tracks, and tears down `connection_struct` instances, which represent per-share tree connections inside an smbd server connection.

## Important APIs, types, and functions
- `conn_new()` allocates a connection, `share_params`, VUID cache, connect path, and synthetic `cwd_fsp`, then links it into `sconn->connections`.
- `conn_num_open()`, `conn_snum_used()`, `conn_protocol()`, and `conn_using_smb2()` expose connection counts, service-use checks, and negotiated protocol checks.
- `conn_clear_vuid_caches()` clears a logged-off VUID from all connections and delegates to `conn_clear_vuid_cache()`.
- `conn_free_internal()` releases VFS handles, pending transaction buffers, zeroes the connection, and resets cwd cache state.
- `conn_setup_case_options()` applies share case-sensitivity and case-preservation options.

## Control flow
Connections are talloc roots linked into the owning `smbd_server_connection`. The talloc destructor removes the connection from the server list, decrements `num_connections`, nulls `sconn`, and runs internal cleanup. VUID cache clearing preserves `conn->session_info` in the special case where it is still referenced for later SMBulogoff/SMBtdis diagnostics and audit paths.

## State and persistence behavior
All state here is in-memory. `conn_new()` initializes `cwd_fsp` as a pseudo FSP with fd `-1` and invalid fnum. `conn_free_internal()` frees VFS per-connection private data and pending trans buffers, then zeroes the structure, so consumers must not access a connection after talloc free.

## Dependencies and integration points
This file depends on talloc, DLIST, loadparm case options, VFS handle lifetime callbacks, `fd_handle_create()`, and server connection globals. It is used by tree connect/disconnect, service reload decisions, SMB1 and SMB2 protocol conditionals, and VUID invalidation.

## Risks and edge cases
- `conn_protocol()` defaults to `PROTOCOL_COREPLUS` if no client connection is available to preserve older behavior.
- Zeroing `connection_struct` in the destructor requires removal from lists first.
- Session info retention for VUID cache clearing is intentional but can surprise ownership readers.
- `cwd_fsp` is a synthetic object; code that assumes all FSPs have real fds must use helper accessors.

## Test signals
Tests should cover connection allocation/free count updates, VUID invalidation across multiple connections, protocol fallback and SMB2 detection, VFS handle `free_data` calls, pending transaction cleanup, and case option setup for auto and explicit case-sensitive shares.
