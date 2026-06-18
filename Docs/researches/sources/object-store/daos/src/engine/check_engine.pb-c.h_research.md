# sources/object-store/daos/src/engine/check_engine.pb-c.h

## Purpose
Generated protobuf-c header for checker engine/control-plane messages. It declares C structs, init macros, serialization APIs, closure typedefs, and descriptors for `check_engine.proto`.

## Important APIs and types
- Request/response structs for checker report, list pool, register pool, and deregister pool methods.
- `Shared__CheckListPoolResp__OnePool` contains pool UUID, label, and repeated service replica ranks.
- `Shared__CheckRegPoolReq` carries sequence, pool UUID, label, and service replicas.
- `Shared__CheckDeregPoolReq` carries sequence and UUID.
- `SHARED__...__INIT` macros initialize embedded `ProtobufCMessage` descriptors and defaults.
- Public functions provide protobuf-c init, size, pack, pack-to-buffer, unpack, and free-unpacked operations.
- Descriptor externs expose reflection metadata to protobuf-c and users.

## Control flow and integration
This header is consumed by `check_engine.pb-c.c` and by engine checker upcall code in `drpc_chk.c`. Callers initialize stack messages with macros, set pointers/counts for dynamic fields, ask for packed size, allocate a buffer, pack into it, and pass it over dRPC. Responses are unpacked with an allocator and freed with the matching `free_unpacked` function.

## State and persistence behavior
The header defines wire-format structures only. It does not own memory except through conventions: string pointers and repeated arrays must remain valid while packing; unpacked messages are owned by protobuf-c allocator and released by `free_unpacked`.

## Dependencies
Requires protobuf-c headers at a compatible version and includes `chk/chk.pb-c.h` for `Chk__CheckReport`. The version guards enforce generator/runtime compatibility.

## Risks
Because this is generated code, hand edits are fragile. Callers must correctly set `n_svcreps` when assigning `svcreps`, must not free borrowed fields before packing, and must not use unpacked strings after `free_unpacked`. Schema drift with control-plane code will break dRPC checker interoperability.

## Test signals
Build tests should catch protobuf-c version mismatch and descriptor symbol availability. Serialization tests should exercise all init macros, empty and nonempty repeated fields, nested `Chk__CheckReport`, and response status propagation.
