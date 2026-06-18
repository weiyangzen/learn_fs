# sources/object-store/daos/src/container/srv_container.c

## Purpose
`srv_container.c` implements the DAOS container service metadata plane. It owns container service initialization, RDB metadata layout, create/destroy/open/close/query dispatch, property and ACL mutation, user attributes, list/filter/upgrade helpers, open-handle accounting, idempotent write replay, metadata timestamps, server-side property changes, and EC aggregation epoch tracking. It is the central bridge between container RPCs from `rpc.h`, pool-service leadership/RDB transactions, security checks, IV cache updates, and target-side collective operations.

## Important APIs, Types, and Functions
- Service lifecycle: `ds_cont_svc_init`, `ds_cont_svc_fini`, `ds_cont_svc_step_up`, `ds_cont_svc_step_down`, `cont_svc_lookup_leader`, `cont_svc_put_leader`, and `ds_cont_bcast_create`.
- Metadata locking/layout: `ds_cont_wrlock_metadata`, `ds_cont_rdlock_metadata`, `ds_cont_unlock_metadata`, and `ds_cont_init_metadata`. The service has root RDB paths for container UUIDs (`cs_uuids`), container KVSs (`cs_conts`), and global container handles (`cs_hdls`).
- Creation and property writing: `cont_create_existence_check`, `cont_create_prop_prepare`, `cont_prop_write`, and `cont_create`.
- Destroy/eviction: `evict_hdls`, `cont_destroy`, `cont_destroy_bcast`, `cont_destroy_post`, and `ds_cont_destroy_orphan`.
- Open/close/query: `cont_open`, `check_hdl_compatibility`, `cont_close_recs`, `cont_close_one_hdl`, `cont_close_hdls`, `cont_close`, `cont_info_read`, `cont_query_bcast`, and `cont_query`.
- Property, ACL, and attributes: `cont_prop_read`, `set_prop`, `check_set_prop_label`, `ds_cont_prop_set`, `ds_cont_acl_update`, `ds_cont_acl_delete`, `cont_attr_set`, `cont_attr_del`, `cont_attr_get`, and `cont_attr_list`.
- Inventory and maintenance: `ds_cont_list`, `ds_cont_filter`, `ds_cont_upgrade`, `ds_cont_rf_check`, `ds_cont_rdb_iterate`, `ds_cont_get_prop`, `ds_cont_hdl_rdb_lookup`, `ds_cont_existence_check`, `ds_cont_iterate_labels`, and `ds_cont_set_label`.
- Dispatch/idempotency: `cont_op_is_write`, `cont_op_lookup`, `cont_op_save`, `cont_op_with_hdl`, `cont_op_with_cont`, `cont_op_with_svc`, `cont_cli_opc_name`, and `ds_cont_op_handler`.
- OID and server-side set-prop: `ds_cont_oid_fetch_add`, `ds_cont_svc_set_prop`, and `ds_cont_set_prop_srv_handler`.
- EC aggregation tracking: `cont_track_eph_leader_*`, `ds_cont_leader_update_track_eph`, `ds_cont_tgt_refresh_track_eph`, `cont_agg_eph_load`, `cont_agg_eph_store`, `cont_agg_eph_sync`, and `ds_cont_svc_refresh_agg_eph`.

## Control Flow
Client RPCs enter through `ds_cont_op_handler`. The handler rejects unexpected server-origin RPCs except server-side `CONT_PROP_SET`, extracts the v9 pool UUID when present, resolves the pool handle, finds the container service leader, and calls `cont_op_with_svc`. Replies always carry `co_rc` and an RSVC hint; open/query property buffers are freed after `crt_reply_send`.

`cont_op_with_svc` starts an RDB transaction, takes a write lock for mutating opcodes and read lock for read-only opcodes, checks duplicate write state for v8+ operation keys, performs container lookup by UUID or label, dispatches to create/open/close/destroy or handle-scoped operations, updates metadata modify time when needed, saves idempotency results through `ds_pool_svc_ops_save`, commits, then performs post-commit side effects such as target destroy and IV refresh. Fault-injection branches simulate no-reply and leader-change retry cases.

Create validates pool permissions, resets pool recovery-container state, merges requested properties into defaults, validates labels and uniqueness across UUID/label indexes, creates the container property KVS, initializes core properties (`ghce`, `alloced_oid`, metadata times, `nhandles`, snapshots, user attrs, handle index, OIT OID KVS), writes all container properties, and inserts the non-default label in `cs_uuids`.

Open validates duplicate handles and exclusive/evict compatibility, rejects unsupported exclusive/evict flags on old pool layout versions, enforces immutable pool and container ACL permissions, optionally evicts existing handles, verifies redundancy status unless forced, updates open metadata time, refreshes property and capability IV entries, records the handle in global `cs_hdls` and per-container `c_hdls`, returns snapshot counts/latest snapshot, handle count, metadata times, and requested properties.

Close invalidates capability IV for the handle, removes the global and per-container handle records, decrements persistent `nhandles`, and marks metadata mtime unless the handle was opened with read-only metadata stats. Batch close paths use a transaction-scoped hash table to cache per-container handle counts because a transaction cannot read back its own uncommitted updates.

Destroy marks a container as `CONTAINER_F_DESTROYING` after checking ACL/delete permissions and evicting handles. After commit, `cont_destroy_post` broadcasts target destroy, opens a new transaction, removes EC tracking, destroys child KVSs, deletes label reverse mapping, destroys the container KVS, and commits. By-label destroy stores the resolved UUID in `ds_pool_svc_op_val.ov_resvd` so duplicate retries do not resolve a reused label to a different container.

Query reads container info, enforces property/ACL access by handle capabilities, optionally fans out a target query, loads requested RDB properties, and verifies/updates health status if `DAOS_PROP_CO_STATUS` is requested. Attribute operations call generic RSVC attr helpers on the per-container user attribute KVS after read/write data capability checks.

## State and Persistence Behavior
Persistent state lives in the pool/container service RDB. Top-level service KVSs are:
- `cs_conts`: maps container UUIDs to per-container property KVSs.
- `cs_uuids`: maps labels to UUIDs.
- `cs_hdls`: maps container handle UUIDs to `struct container_hdl`.

Each container property KVS stores layout/checksum/redundancy/snapshot/compression/encryption/dedup/ACL/owner/root/status/OID/version/scrubber properties, `ghce` flags, allocated OID counter, snapshot count and snapshot KVS, user attrs KVS, per-container handle index, OIT OID KVS, metadata open/modify times, and persistent open-handle count on upgraded layouts.

In-memory service state includes RDB paths, the service lock, `cs_pool`, and the EC aggregation leader list. IV state mirrors container properties, capabilities, snapshots, and tracked epochs for fast distributed access. Metrics counters record successful create/open/close/query/destroy paths.

## Dependencies and Integration Points
This file depends heavily on DAOS pool services (`ds_pool_*`, pool maps, pool handle credentials), RDB transactions and KVS paths, security/ACL helpers (`ds_sec_*`, `daos_acl_*`), IV update helpers (`cont_iv_*`), target/container child state, VOS stable epoch calls, scheduler ULTs, telemetry metrics, and RPC declarations from `rpc.h`. Snapshot and OIT functions are implemented in adjacent container files but dispatched here. Target-side destroy/query/snapshot/epoch aggregate are reached through collective RPCs created by `ds_cont_bcast_create`.

## Risks and Edge Cases
- Idempotency is subtle. Write operations from protocol v8+ are replayed using client UUID and HLC time; duplicate by-label destroy must use the saved UUID, not a fresh label lookup.
- RDB lock and transaction boundaries matter. Post-destroy target broadcast intentionally happens outside the first transaction, then metadata deletion happens in a second transaction.
- Persistent `nhandles` updates are cached during batch close to avoid transaction read-your-write limitations. Any new batch handle mutation must preserve that behavior.
- Label mutations must keep `cs_uuids` and the property KVS consistent. Reused or mismatched labels are treated as errors.
- Layout upgrades are version-gated. Old pools may lack metadata times, nhandles, exclusive/evict support, OIT OID KVS, or newer properties; code often treats `-DER_NONEXIST` as a defaulted property only for known upgrade gaps.
- Security is split between pool permissions, container ACL-derived capabilities, handle capabilities, and admin server-side paths. New operations must choose the correct capability check.
- IV cache updates occur both inside main operation paths and after commit. Missing an IV update can leave clients with stale properties/capabilities/snapshots.
- EC aggregation tracking is asynchronous, leader-only, and pool-map-sensitive. Rank changes can force leader tracking records to be deleted/recreated, and sluggish reporting only warns after thresholds.
- Many paths use fault injection macros, so tests may depend on exact failure timing and return codes.

## Test Signals
High-value tests include create/open/query/close/destroy integration tests, by-label create/open/destroy/property-set including duplicate retry with label reuse, ACL and immutable pool permission tests, exclusive/evict handle compatibility tests, persistent handle count and metadata timestamp checks, pool-layout upgrade tests, property IV consistency checks, container list/filter tests, OID allocation monotonicity tests, target destroy failure/retry tests, EC aggregation epoch refresh tests, and fault-injection tests for no-reply/leader-change/idempotent replay paths.
