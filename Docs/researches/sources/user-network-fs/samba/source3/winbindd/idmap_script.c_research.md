# sources/user-network-fs/samba/source3/winbindd/idmap_script.c

## Purpose
This read-only backend delegates SID/Unix-ID mapping to an external script. It supports `SIDTOID <sid>` and `IDTOSID <type> <id>` commands and parses `XID:`, `UID:`, `GID:`, `SID:`, or unmapped/error output.

## Important APIs, Types, And Functions
`struct idmap_script_context` stores the script path. Async helpers `idmap_script_xid2sid_send/recv` and `idmap_script_sid2xid_send/recv` execute one script call via `file_ploadv_send`. Batch helpers `idmap_script_xids2sids` and `idmap_script_sids2xids` run a temporary tevent loop. Backend methods are `idmap_script_unixids_to_sids`, `idmap_script_sids_to_unixids`, and `idmap_script_db_init`. `idmap_script_init` registers the backend.

## Control Flow
Initialization reads `idmap config <domain> : script`, falls back to deprecated `idmap:script` for the default domain, talloc-copies the script path, and marks the domain read-only. Unix-ID-to-SID initializes statuses, launches one child process per requested ID, parses null-terminated output up to 1024 bytes, and returns aggregate all/some/none mapped status. SID-to-ID follows the same pattern and filters returned IDs against the configured idmap range.

## State And Persistence
The backend stores only the script path in memory. Persistent or authoritative mapping state is external to Samba and owned by the script or its backing store.

## Dependencies And Integration
It depends on tevent, `file_ploadv_send`, Samba argument-list helpers, SID parsing, idmap range utilities, and Unix-to-NT error mapping. It integrates as a normal idmap backend but does not allocate.

## Risks And Test Signals
Test missing script config, invalid ID type, nonzero child execution errors, empty output, non-null-terminated output, oversized output, malformed `SID:`/`UID:`/`GID:`/`XID:` lines, mixed batches, and range filtering. `idmap_script_db_init` logs `ctx->script` before it is assigned, so debug output can be misleading or null. Running many IDs spawns many subprocesses concurrently in the temporary tevent loop, which needs load/error tests.
