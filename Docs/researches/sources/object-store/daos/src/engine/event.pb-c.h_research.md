# sources/object-store/daos/src/engine/event.pb-c.h

## Purpose
Generated protobuf-c header for `event.proto`. It defines the C ABI used by DAOS engine/control-plane code to serialize and deserialize RAS cluster event notifications. The file is not handwritten business logic, but it is an integration contract: field numbers, oneof cases, init macros, and descriptors must match the `.proto` schema and the generated implementation.

## Important APIs, Types, and Functions
The primary types are `Shared__RASEvent`, `Shared__RASEvent__EngineStateEventInfo`, `Shared__RASEvent__PoolSvcEventInfo`, `Shared__ClusterEventReq`, and `Shared__ClusterEventResp`. `Shared__RASEvent__ExtendedInfoCase` models the protobuf oneof for opaque string data, engine-state details, or pool-service details. Generated methods include `*_init`, `*_get_packed_size`, `*_pack`, `*_pack_to_buffer`, `*_unpack`, and `*_free_unpacked` for the top-level event, request, and response messages. External descriptors such as `shared__rasevent__descriptor` are consumed by protobuf-c runtime calls.

## Control Flow
Callers initialize stack or heap messages with the generated `*_INIT` macros or `*_init` functions, fill scalar fields and pointer fields, then ask protobuf-c to pack them into a byte buffer. Receivers call `*_unpack`, inspect required fields and the `extended_info_case`, and release allocations with `*_free_unpacked`. Nested engine-state and pool-service structures are referenced by pointer from `Shared__RASEvent`.

## State and Persistence Behavior
This header owns no runtime state and persists nothing. It defines serialized state exchanged across process boundaries. The durable compatibility concern is wire-level schema stability: field numbers and oneof tags are effectively persistent API. Strings default to `protobuf_c_empty_string`, and repeated service-rank arrays are represented by `n_*` plus pointer pairs.

## Dependencies and Integration Points
The only direct dependency is `protobuf-c/protobuf-c.h`, with version guards requiring protobuf-c headers compatible with protoc-c output. DAOS RAS notification producers and consumers use this contract to communicate event identifiers, severity, host/rank/incarnation context, job/pool/container/object identifiers, control operation hints, and optional extended event data.

## Risks
Manual edits will be overwritten by regeneration and may desynchronize the C ABI from `event.proto`. Callers must keep the oneof discriminator consistent with the active union member. Pointer fields require lifetime care until packing completes. Schema changes can break older control-plane binaries if field semantics or required interpretation changes without compatibility handling.

## Test Signals
Useful tests are protobuf round trips for each event shape, control-plane compatibility tests using real RAS events, version-skew checks for generated files, and negative unpack tests for missing or unknown extended information. Build failures around descriptor symbols or protobuf-c version guards are also strong integration signals.
