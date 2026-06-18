# sources/object-store/daos/src/container/srv_epoch.c

## Purpose
Implements container epoch and snapshot service operations on the pool/container service leader. It owns the RDB-backed snapshot list, snapshot object-index-table (OIT) OID metadata, and the service-side paths for create/list/destroy snapshot RPCs. It also coordinates target notification before committing snapshot metadata so target VOS/OIT state is prepared consistently.

## Important APIs and functions
- `ds_cont_epoch_aggregate()` validates write capability and normalizes an aggregate epoch, but target aggregation is effectively a placeholder in the paired target file.
- `ds_cont_snap_create()` checks write permission, calls `snap_create_bcast()`, returns the selected snapshot epoch, and stores it in the idempotence operation value.
- `ds_cont_snap_list()` returns snapshot count and optionally bulk-transfers snapshot epochs.
- `ds_cont_snap_destroy()` deletes a snapshot key, removes any OIT-OID key for that epoch, and decrements `ds_cont_prop_nsnapshots`.
- `ds_cont_get_snapshots()` is an internal leader-side helper for other xstreams/modules.
- `ds_cont_update_snap_iv()` refreshes snapshot IV state from RDB and publishes it through `cont_iv_snapshots_update()`.
- `ds_cont_snap_oit_create()`, `ds_cont_snap_oit_destroy()`, and `ds_cont_snap_oit_oid_get()` manage the snapshot-to-OIT-object mapping.

## Control flow
Snapshot creation parses epoch/options from the RPC, checks container write capability, and uses `snap_oit_create()` to broadcast `CONT_TGT_SNAPSHOT_NOTIFY` to targets. That target notification can create OIT content and can replace the requested epoch with current HLC for create options. Only after successful target notification does `snap_create_bcast()` update `cont->c_snaps` and increment `nsnapshots` in the container property KVS. Listing uses `read_snap_list()`, which iterates `cont->c_snaps`, grows a heap buffer, and returns the total count even when the caller's bulk buffer is smaller. If a bulk handle is supplied, `xfer_snap_list()` creates a local bulk handle and performs `CRT_BULK_PUT` to the client.

## State and persistence
Persistent state lives in RDB paths carried by `struct cont`: `c_snaps` stores snapshot epochs as integer keys with a nonempty dummy value, `c_prop` stores `nsnapshots`, and `c_oit_oids` stores `epoch -> daos_obj_id_t` for OIT snapshots when container global version supports it. Snapshot IV is derived, not authoritative; it is refreshed after RDB changes and consumed by targets for aggregation boundaries.

## Dependencies and integration points
Depends on RDB transactions, container layout keys from `srv_layout.h`, security checks from `daos_srv/security.h`, CaRT RPC helpers from `rpc.h`, target broadcast via `ds_cont_bcast_create()`, pool map placement for OIT generation, and IV update helpers from `container_iv.c`. The OIT path integrates with `srv_oi_table.c` on targets.

## Risks
`ds_cont_epoch_aggregate()` currently does little beyond validation, so callers may assume more aggregation work than is present. Snapshot create performs target-side OIT work before RDB snapshot insertion; failures after target work but before RDB commit need idempotence/retry behavior to be correct. `ds_cont_snap_destroy()` decrements `nsnapshots` without underflow guard after the existence lookup. Bulk listing returns total snapshot count while transferring only up to provided capacity, which callers must interpret correctly. `ds_cont_update_snap_iv()` logs and ignores IV failures, so aggregation may temporarily run with stale snapshot boundaries.

## Test signals
Useful tests should cover permission denial, invalid epochs, bounded and unbounded snapshot listing, bulk transfer truncation/count semantics, OIT OID lookup for old/new container versions, RDB failure paths, and IV refresh after create/destroy. Integration tests should verify target notification failure prevents RDB snapshot insertion.
