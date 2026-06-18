# sources/object-store/daos/src/engine/event.pb-c.c

## Purpose
Generated protobuf-c implementation for RAS event messages from `event.proto`. It provides serialization APIs and descriptors for engine/control-plane RAS event traffic.

## Important APIs and descriptors
Generated functions cover `Shared__RASEvent__EngineStateEventInfo`, `Shared__RASEvent__PoolSvcEventInfo`, `Shared__RASEvent`, `Shared__ClusterEventReq`, and `Shared__ClusterEventResp`. The main event descriptor has 19 fields, including id, message, timestamp, type, severity, hostname, rank, incarnation, hardware/process/thread/job/pool/container/object/control-operation fields, and a oneof extended info (`str_info`, `engine_state_info`, `pool_svc_info`).

## Control flow
Init functions assign static init templates. Size/pack/pack-to-buffer/unpack/free helpers assert descriptor identity and delegate to protobuf-c. Descriptor tables define field names, field numbers, labels, types, struct offsets, default strings, oneof case offsets, nested descriptors, name indexes, and number ranges. Cluster event request/response descriptors wrap a sequence number plus event or status.

## State and persistence behavior
No mutable DAOS state. Static descriptors encode the protobuf wire schema used by `drpc_ras.c` and the control plane. Serialized events become dRPC payloads and then external RAS/control-plane records.

## Dependencies and integration
Includes `event.pb-c.h` and protobuf-c. `drpc_ras.c` uses `shared__cluster_event_req__get_packed_size()` and `shared__cluster_event_req__pack()` to send events; typed event info descriptors support pool service and engine state events.

## Risks
Generated files must stay synchronized with `event.proto` and remote consumers. Oneof fields depend on setting `extended_info_case` correctly; forgetting it can silently omit extended data. Manual edits are unsafe. Field number changes are wire incompatible.

## Test signals
Tests should pack/unpack generic string-info events, pool service events with repeated ranks, engine state events, empty optional fields, and cluster responses with nonzero status. Regeneration checks should detect drift from `event.proto`.
