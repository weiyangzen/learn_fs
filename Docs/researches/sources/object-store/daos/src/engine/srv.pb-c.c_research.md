# sources/object-store/daos/src/engine/srv.pb-c.c

## Purpose
Generated protobuf-c implementation for `srv.proto`. It provides message initialization, packing, unpacking, freeing, and descriptor metadata for dRPC messages exchanged between DAOS I/O engines and the control server.

## Important APIs, Types, and Functions
The file implements generated functions for `Srv__NotifyReadyReq`, `Srv__GetPoolSvcReq`, `Srv__GetPoolSvcResp`, `Srv__PoolFindByLabelReq`, `Srv__PoolFindByLabelResp`, `Srv__ListPoolsReq`, `Srv__ListPoolsResp__Pool`, and `Srv__ListPoolsResp`. It also defines `ProtobufCFieldDescriptor`, field index, range, and `ProtobufCMessageDescriptor` objects for each message.

## Control Flow
Each `*_init` copies a static init macro into the caller-provided struct. `*_get_packed_size`, `*_pack`, and `*_pack_to_buffer` assert the descriptor and delegate to protobuf-c runtime helpers. `*_unpack` delegates to `protobuf_c_message_unpack` with the matching descriptor. `*_free_unpacked` checks for NULL, asserts the descriptor, and releases unpacked memory through protobuf-c.

## State and Persistence Behavior
There is no mutable application state. Static const descriptors encode the wire contract: field names, field numbers, labels, C offsets, default values, packed repeated scalar flags, nested message descriptors, and package/name metadata. Serialized messages may persist in dRPC buffers only for the duration of request handling.

## Dependencies and Integration Points
The file includes `srv.pb-c.h` and uses protobuf-c runtime internals. dRPC client/server code uses these functions for notify-ready, pool service lookup, pool label lookup, and pool listing messages. `init.c` indirectly depends on `NotifyReadyReq` through `drpc_notify_ready`.

## Risks
Because this is generated code, manual edits risk divergence from `srv.proto`. ABI risks come from mismatched generated header/source versions, protobuf-c version mismatches, or schema changes that reuse field numbers incorrectly. Callers must supply arrays matching `n_*` counts for repeated fields and must not pass uninitialized messages to pack routines.

## Test Signals
Generated-code tests should focus on schema round trips for every message, packed repeated `uint32` service-rank arrays, nested `ListPoolsResp.Pool` messages, compatibility between generated header and source descriptors, and dRPC integration tests for ready notification and pool queries.
