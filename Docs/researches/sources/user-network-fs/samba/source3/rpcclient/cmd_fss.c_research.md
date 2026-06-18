# sources/user-network-fs/samba/source3/rpcclient/cmd_fss.c

## Purpose
`cmd_fss.c` implements rpcclient commands for the File Server Remote VSS Protocol (FSRVP). It checks shadow-copy support, creates and exposes shadow-copy sets, deletes exposed mappings, queries mappings, detects whether a path is shadow copied, and marks recovery complete.

## Important APIs, types, and functions
- `fss_errors[]`, `get_error_str()`, `struct fss_context_map`, `ctx_map[]`, and `map_fss_ctx_str()` translate FSRVP/HRESULT status and user context names.
- `cmd_fss_is_path_sup()` and `cmd_fss_get_sup_version()` query provider support and supported protocol versions.
- `cmd_fss_create_expose_parse()` parses context, read-only/read-write mode, and share arguments into UNC mapping requests.
- `cmd_fss_create_expose()` orchestrates `IsPathSupported`, `GetSupportedVersion`, `SetContext`, `StartShadowCopySet`, `AddToShadowCopySet`, `PrepareShadowCopySet`, `CommitShadowCopySet`, `ExposeShadowCopySet`, and `GetShareMapping`.
- `cmd_fss_abort()` aborts a shadow-copy set on mid-flow failures.
- `cmd_fss_delete()`, `cmd_fss_is_shadow_copied()`, `cmd_fss_get_mapping()`, and `cmd_fss_recov_complete()` wrap individual management calls.

## Control flow
The create/expose command is a multi-step transaction. It parses and validates the requested context and shares, extends the DCE/RPC timeout for slow VSS calls, verifies each share supports FSRVP, sets context, starts a set with a random client GUID, adds each share with random copy GUIDs, prepares and commits the set with long timeouts, exposes the set, then queries and prints each exposed mapping. If add, prepare, or commit fails after a set exists, it attempts `AbortShadowCopySet`.

## State and persistence behavior
Support/version/query commands are read-only. Create/expose creates remote shadow copies and exposed shares; delete removes exposed mappings; recovery-complete changes server-side shadow-copy-set state. Locally, only transient GUIDs and mapping arrays are stored.

## Dependencies and integration points
The module depends on generated FSRVP client stubs, HRESULT utilities, Samba GUID/time helpers, rpcclient server name fields, and DCE/RPC binding timeout control. It pairs with the source3 `RPC_FSS_AGENT` and `rpcd_fsrvp` build targets.

## Risks and edge cases
- Create/expose is a high-impact remote storage operation; partial failures can leave shadow copies or exposed mappings if abort is not reached or fails.
- Timeout units are transport-sensitive, and the code comments call out source3/source4 unit differences.
- UNC construction differs between `cli->srv_name_slash` and `cli->desthost`; inconsistent naming can affect server matching.
- `SupportedByThisProvider` is a pointer in generated output; the code assumes it is non-NULL on success.
- Context flags combine user context with `ATTR_AUTO_RECOVERY` for read-write mode, so parsing mistakes alter snapshot semantics.

## Test signals
Use a disposable FSRVP-capable server and share. Test support/version commands, create/expose for read-only and read-write contexts, multi-share sets, delete mapping, get mapping, has-shadow-copy, and recovery-complete. Failure injection should cover unsupported shares, timeouts, invalid GUIDs, and permission-denied responses.
