# sources/object-store/daos/src/engine/srv.pb-c.h

## Purpose
Generated protobuf-c header for `srv.proto`. It defines C structs, init macros, method prototypes, closure types, and descriptors for DAOS engine dRPC service messages.

## Important APIs, Types, and Functions
Messages include `Srv__NotifyReadyReq`, `Srv__GetPoolSvcReq`, `Srv__GetPoolSvcResp`, `Srv__PoolFindByLabelReq`, `Srv__PoolFindByLabelResp`, `Srv__ListPoolsReq`, `Srv__ListPoolsResp`, and nested `Srv__ListPoolsResp__Pool`. Generated methods cover initialization, packed-size calculation, packing, buffer packing, unpacking, and freeing for all top-level messages; the nested pool message has an init helper and descriptor.

## Control Flow
Callers build requests/responses by initializing structs, assigning scalar and pointer fields, setting `n_*` counts for repeated values, then packing via protobuf-c. Receivers unpack bytes to generated structs, inspect status/UUID/service-rank/list fields, and free unpacked messages with the generated free helpers.

## State and Persistence Behavior
The header defines serialized state but owns no live state. `NotifyReadyReq` carries engine runtime metadata such as primary/secondary CART URIs, context counts, dRPC listener socket, instance index, target count, HLC incarnation, and check-mode flag. Pool query responses carry DAOS status codes and service rank arrays.

## Dependencies and Integration Points
The file depends on protobuf-c headers and version guards. It is consumed by dRPC code connecting the engine to the control server, especially startup readiness and management pool lookup/listing operations.

## Risks
The repeated fields require correct `n_secondaryuris`, `n_secondarynctxs`, `n_svcreps`, and `n_pools` counts. The generated C field names encode proto names such as `drpcListenerSock` as `drpclistenersock`, so handwritten callers must use the generated names. Schema evolution must preserve wire compatibility for control-plane/engine version skew.

## Test Signals
Tests should verify message initialization defaults, notify-ready payloads with secondary providers, pool service response arrays, list-pools nested messages, unpack/free behavior under custom allocators, and build-time protobuf-c version compatibility.
