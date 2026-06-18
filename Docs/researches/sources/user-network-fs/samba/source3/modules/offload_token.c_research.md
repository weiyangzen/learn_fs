# sources/user-network-fs/samba/source3/modules/offload_token.c

## Purpose
Implements in-process ODX/copy-offload token storage and validation. It lets VFS modules create opaque resume/copy tokens, map them back to open `files_struct` handles, and enforce SMB access rules before server-side copy operations.

## APIs, Types, And Control Flow
`vfs_offload_token_ctx_init()` lazily creates a `vfs_offload_ctx` with an in-memory rbt dbwrap database. `vfs_offload_token_create_blob()` creates 20-byte or 24-byte tokens containing persistent id, volatile id, and fsctl code at fixed offsets. `vfs_offload_token_db_store_fsp()` stores a token-to-fsp pointer under db lock and attaches a `fsp_token_link` destructor to delete the record when the file handle is freed. `vfs_offload_token_db_fetch_fsp()` parses the record back to a typed `files_struct *`. `vfs_offload_token_check_handles()` enforces same session, valid and non-closing handles, non-directory and non-IPC/PRINT shares, writable destination, and readable source.

## State, Dependencies, Integration
State is per-context in-memory dbwrap data, lifetime-bound to the Samba client or module context. No token database survives process lifetime. Dependencies include dbwrap rbt, talloc destructors, SMB2 file handle structures, access-check helpers, and FSCTL constants. Integrated by `vfs_default.c`, `vfs_btrfs.c`, and `vfs_fruit.c`.

## Risks And Test Signals
Tokens contain handle IDs but the authoritative lookup is an in-memory pointer, so process restart or handle destruction invalidates them. Pointer serialization requires record size validation and talloc type checking. Tests should cover duplicate token store for same and different fsp, destructor cleanup, unknown tokens, malformed db values, each access-denied branch, FSCTL length selection, and copychunk-specific destination read checks.
