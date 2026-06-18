# sources/user-network-fs/samba/source4/torture/local/fsrvp_state.c

## Purpose
This file tests persistence and retrieval of File Server Remote VSS Protocol state used by Samba's FSRVP server.

## Important APIs, types, and functions
It builds `fss_global`, `fss_sc_set`, `fss_sc`, and `fss_sc_smap` structures, then calls `fss_state_store()` and `fss_state_retrieve()`. Helper constructors create random GUID-backed shadow-copy sets, shadow copies, and share mappings. Compare helpers validate GUIDs, strings, states, contexts, timestamps, counts, and linked-list membership.

## Control flow
`test_fsrvp_state_empty()` stores and retrieves an empty state file. `test_fsrvp_state_single()` builds a one-set/one-copy/one-share-map hierarchy and compares after retrieval. `test_fsrvp_state_multi()` builds multiple sets, copies, and mappings and compares order-insensitively by GUID/share name. `test_fsrvp_state_none()` retrieves from a missing state path and expects an empty result. `torture_local_fsrvp()` registers the cases.

## State and persistence behavior
Each test creates a temporary directory with `mkdtemp`, writes an FSRVP TDB state file named by `FSS_DB_NAME`, retrieves it into a fresh memory context, then unlinks the file and removes the directory. The persisted state includes IDs, state enums, context values, volume paths, timestamps, and share mappings.

## Dependencies and integration points
The file depends on `source3/rpc_server/fss/srv_fss_private.h`, FSRVP NDR types, dlinklist helpers, NTSTATUS assertions, and smbtorture local registration. It directly validates private FSS state serialization used by the RPC server.

## Risks and edge cases
The tests require temporary directory cleanup to succeed and use wall-clock `time(NULL)` for timestamps. Comparisons rely on unique GUIDs/share names to match list entries. `torture_local_fsrvp()` creates a stackframe because dbwrap uses `talloc_tos()`.

## Test signals
Passing tests indicate empty, absent, simple, and complex FSRVP state trees survive store/retrieve cycles with structure and values intact.
