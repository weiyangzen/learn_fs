# sources/user-network-fs/davfs2/src/webdav.h

## Purpose
`webdav.h` declares the davfs2 WebDAV transport interface and the `dav_props` result structure used by higher layers to reason about remote resources. It documents the contract for initialization, file/resource operations, locking, quota, encoding conversion, and cleanup.

## Important APIs, Types, and Functions
- `struct dav_props`: linked-list node with unescaped `path`, basename-like `name`, normalized `etag`, `size`, `mtime`, `is_dir`, `is_exec`, and `next`.
- Initialization/cleanup: `dav_init_webdav`, `dav_init_connection`, `dav_close_webdav`, `dav_set_no_terminal`.
- Conversion: `dav_conv_from_utf_8`, `dav_conv_to_utf_8`, `dav_conv_from_server_enc`, `dav_conv_to_server_enc`.
- Resource operations: `dav_get_collection`, `dav_get_file`, `dav_head`, `dav_delete`, `dav_delete_dir`, `dav_make_collection`, `dav_move`, `dav_put`, `dav_quota`, `dav_set_execute`.
- Lock operations: `dav_lock`, `dav_lock_refresh`, `dav_unlock`.
- Error access: `dav_get_webdav_error()`.

## Control Flow
Callers initialize once with `dav_init_webdav(args)`, then either explicitly call `dav_init_connection(path)` or let public operations lazily initialize. Directory listings return caller-owned linked lists. File GET/PUT and metadata methods update caller-provided etag, mtime, length, existence, expiration, and modified flags only on documented success paths. Lock-related operations are no-ops when initialized with `nolocks`.

## State and Persistence
The header exposes no state directly, but all functions operate on `webdav.c` global session state. Returned strings and `dav_props` lists are heap-owned by the caller and must be freed with `dav_delete_props()` node-by-node. Operations mutate remote WebDAV state and local cache files.

## Dependencies and Integration Points
The interface depends on `dav_args` from `mount_davfs.h`, POSIX `off_t`, `time_t`, and `uint64_t`, and is used by davfs cache/kernel operation code. It abstracts Neon-specific details from upper layers by returning errno-style integers.

## Risks and Edge Cases
The contract assumes a single initialized global session; no handle is passed to distinguish multiple sessions. Many output parameters are optional, so callers must preserve old state on error and check return codes. `dav_delete_props()` frees only one list node despite the common list result from `dav_get_collection()`. Header comments mention a `mime` parameter in some places where the signature no longer includes one, indicating stale documentation around `dav_head`/`dav_put`.

## Test Signals
Interface-level tests should verify ownership conventions, optional output parameter handling, no-lock behavior, lazy connection initialization, and that callers free entire property lists. Header/API consistency checks should flag stale comments when signatures change.
