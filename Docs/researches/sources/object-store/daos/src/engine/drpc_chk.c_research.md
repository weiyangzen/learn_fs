# sources/object-store/daos/src/engine/drpc_chk.c

## Purpose
Implements checker-related dRPC client upcalls from the engine to the control plane. It lets checker code list known pools, register or refresh pool metadata, deregister pools, and report checker findings.

## Important APIs
- `ds_chk_free_pool_list()` frees `struct chk_list_pool` arrays returned by listpool.
- `ds_chk_listpool_upcall()` calls `DRPC_METHOD_CHK_LIST_POOL` and converts protobuf pool entries to DAOS checker structures.
- `ds_chk_regpool_upcall()` calls `DRPC_METHOD_CHK_REG_POOL` with sequence, UUID string, label, and service replicas.
- `ds_chk_deregpool_upcall()` calls `DRPC_METHOD_CHK_DEREG_POOL`.
- `ds_chk_report_upcall()` sends a `Chk__CheckReport` payload through `DRPC_METHOD_CHK_REPORT`.

## Control flow
Each upcall initializes a generated protobuf request, computes packed size, allocates a request buffer, packs, calls `dss_drpc_call(DRPC_MODULE_SRV, method, ...)`, checks dRPC transport status, unpacks the protobuf response with `PROTO_ALLOCATOR_INIT`, checks allocator OOM/NULL response, extracts DAOS status, then frees response/request resources. Listpool additionally allocates an array of checker pool records, parses UUID strings, duplicates labels, converts repeated `uint32_t` service replicas to `d_rank_list_t`, and transfers ownership to the caller on success.

## State and persistence behavior
No local persistent state. The functions translate between local checker state and management-service state held by daos_server/control plane. Returned pool lists are heap state owned by the caller and freed with `ds_chk_free_pool_list()`.

## Dependencies and integration
Depends on checker server headers, dRPC module IDs/method IDs, `dss_drpc_call()` from `drpc_client.c`, generated checker protobuf bindings, UUID parsing/formatting, rank-list conversion helpers, and DAOS fail injection (`DAOS_CHK_LEADER_FAIL_REGPOOL`).

## Risks
The code treats pack return values as `int rc` in places even though protobuf-c pack returns `size_t`; negative checks are ineffective for unsigned return semantics. Listpool cleanup uses `respb->n_pools` when freeing partially initialized local arrays, so `ds_chk_free_pool_list()` must tolerate NULL fields. A dRPC success status can still carry a protobuf-level DAOS error, and callers need to handle positive list count versus negative error return from `ds_chk_listpool_upcall()`.

## Test signals
Tests should mock `dss_drpc_call()` for transport failure, non-success dRPC status, unpack OOM/NULL, response status errors, malformed UUIDs, allocation failure during label/rank conversion, fail-injection register errors, and successful ownership transfer/free of pool lists.
