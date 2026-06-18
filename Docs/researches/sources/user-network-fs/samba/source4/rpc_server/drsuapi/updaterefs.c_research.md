# sources/user-network-fs/samba/source4/rpc_server/drsuapi/updaterefs.c

## Purpose
`updaterefs.c` implements `IDL_DRSUpdateRefs`, the RPC used to add or remove a destination DSA from an NC's `repsTo` list. It also exposes `drsuapi_UpdateRefs()` as an internal helper so other replication code, notably `DsGetNCChanges`, can re-establish monitoring references without going back through the public RPC handler.

The file validates request shape and NC identity, enforces topology-management access in the RPC entry point, updates `repsTo` transactionally, and asks `dreplsrv` to refresh after successful changes.

## Important APIs, Types, and Functions
- `struct repsTo` wraps the `repsFromToBlob` array and count loaded from the `repsTo` attribute.
- `uref_check_dest()` loads current `repsTo` and checks whether the destination DSA GUID already exists, returning `REF_ALREADY_EXISTS` or `REF_NOT_FOUND` unless combined add/delete or `GETCHG_CHECK` semantics allow idempotence.
- `uref_add_dest()` appends a version-1 `repsFromToBlob`, copies the caller-provided `repsFromTo1`, propagates `DRSUAPI_DRS_REF_GCSPN`, and saves the modified `repsTo`.
- `uref_del_dest()` removes all matching destination GUID entries from `repsTo`, compacts the array with `memmove()`, saves the result, and handles idempotent delete behavior.
- `drsuapi_UpdateRefs()` is the shared implementation used by RPC and internal callers. It validates input, resolves the requested object identifier to an NC root, applies add/delete updates inside an LDB transaction, and sends an IRPC refresh to `dreplsrv`.
- `dcesrv_drsuapi_DsReplicaUpdateRefs()` is the public RPC wrapper. It pulls the DRS bind handle, checks request level, enforces `GUID_DRS_MANAGE_TOPOLOGY`, validates non-admin DSA ownership, and delegates to `drsuapi_UpdateRefs()`.

## Control Flow
The RPC handler accepts only level 1. It checks topology-management access against the request naming context. If the caller is below administrator level, it requires that `dest_dsa_guid` belongs to the caller's SID via `dsdb_validate_dsa_guid()`. On success it calls the shared helper with the server messaging and event contexts.

`drsuapi_UpdateRefs()` first chooses `sam_ctx_system` when available, otherwise the normal SAM DB context. It rejects an all-zero destination GUID, a missing DNS name, and requests that specify neither add nor delete. It converts the supplied object identifier to both a normalized DN and NC root, then requires them to match. This prevents callers from updating references on arbitrary child objects.

The helper performs a preflight `uref_check_dest()` before opening a transaction. Existing/not-found errors are suppressed only when `DRSUAPI_DRS_GETCHG_CHECK` makes the operation idempotent. Inside the transaction it performs delete first, then add, based on option bits. A failure cancels the transaction and returns the underlying WERROR. A successful commit is followed by a best-effort IRPC `dreplsrv_refresh` notification.

## State and Persistence Behavior
The durable state is the NC root's `repsTo` attribute in the DSDB. Updates are written through `dsdb_savereps()` inside an LDB transaction. Add/delete in a single request is supported and delete runs first, which lets callers replace an existing reference with updated flags/data.

The `drepl_refresh_state` exists only long enough to send an IRPC refresh. If `dreplsrv` is not running or allocation fails, the function returns `WERR_OK` after the database commit; refresh is best effort and not part of the transaction.

## Dependencies and Integration Points
This file depends on the DCE/RPC server framework, DSDB SAM APIs, DRSUAPI NDR types, security/session helpers, IRPC generated client stubs, and Samba messaging. It integrates with `getncchanges.c` because `DsGetNCChanges` can call `drsuapi_UpdateRefs()` when clients set `DRSUAPI_DRS_ADD_REF` or `DRSUAPI_DRS_REF_GCSPN`. It also integrates with `dreplsrv` via `irpc_binding_handle_by_name()` and `dcerpc_dreplsrv_refresh_r_send()`.

## Risks and Edge Cases
- Request options are bitwise and can request both add and delete. The behavior is intentional, but tests must verify replacement semantics and idempotence under `GETCHG_CHECK`.
- `uref_del_dest()` removes every matching GUID, not just the first. That is probably correct cleanup behavior, but it can hide prior duplication issues.
- Refresh notification is best effort. A successful return does not prove `dreplsrv` observed the change immediately.
- The helper trusts `dest_dsa_dns_name` after only NULL validation; comments note that length validation is missing.
- Non-admin ownership validation happens only in the RPC wrapper. Internal callers must already have performed appropriate access checks before invoking `drsuapi_UpdateRefs()`.

## Test Signals
Tests should cover invalid parameters, non-NC object rejection, add of new `repsTo`, duplicate add, delete of existing reference, delete of missing reference, add+delete replacement, `GETCHG_CHECK` idempotence, `DRS_REF_GCSPN` flag propagation, transaction rollback on save failure, non-admin DSA ownership rejection, and a successful path with and without a running `dreplsrv` IRPC endpoint.
