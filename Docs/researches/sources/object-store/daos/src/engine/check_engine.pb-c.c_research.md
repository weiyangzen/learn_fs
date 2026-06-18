# sources/object-store/daos/src/engine/check_engine.pb-c.c

## Purpose
Generated protobuf-c implementation for `check_engine.proto`. It provides initialization, packing, unpacking, freeing, field descriptors, and message descriptors for checker dRPC request/response messages exchanged between the DAOS engine and control plane.

## Important APIs and descriptors
The generated functions cover `Shared__CheckReportReq`, `Shared__CheckReportResp`, `Shared__CheckListPoolReq`, `Shared__CheckListPoolResp__OnePool`, `Shared__CheckListPoolResp`, `Shared__CheckRegPoolReq`, `Shared__CheckRegPoolResp`, `Shared__CheckDeregPoolReq`, and `Shared__CheckDeregPoolResp`. Each nontrivial message gets `__init`, `__get_packed_size`, `__pack`, `__pack_to_buffer`, `__unpack`, and `__free_unpacked` functions. The file exports descriptors such as `shared__check_reg_pool_req__descriptor` and nested field descriptor tables.

## Control flow
Every init function assigns a static `*_INIT` value. Pack/size functions assert the message descriptor pointer matches the expected descriptor and delegate to protobuf-c. Unpack delegates to `protobuf_c_message_unpack()` with the corresponding descriptor. Free functions ignore NULL, assert descriptor identity, and delegate to `protobuf_c_message_free_unpacked()`. The bottom half defines field descriptor arrays, name indexes, number ranges, and `ProtobufCMessageDescriptor` instances used by protobuf-c reflection.

## State and persistence behavior
There is no mutable DAOS state. The only state is static descriptor metadata compiled into the binary. Serialized bytes produced by these helpers are the wire format consumed by dRPC checker methods.

## Dependencies and integration
Includes `check_engine.pb-c.h`, which includes `chk/chk.pb-c.h` for the nested `Chk__CheckReport` report payload. `drpc_chk.c` directly uses these helpers to encode list/register/deregister/report upcalls and decode control-plane responses.

## Risks
This file must match the generated header and the `.proto` schema used by the control plane. Manual edits would be overwritten and can create ABI/wire incompatibility. Descriptor assertions catch wrong message types in debug builds, but release behavior depends on protobuf-c. Repeated rank arrays are marked packed in the generated descriptor; peers must use compatible protobuf definitions.

## Test signals
Regeneration tests should verify generated files are up to date with `check_engine.proto`. Runtime tests should pack/unpack each checker message, including empty list requests, repeated service rank arrays, nested report payloads, and nonzero DAOS status fields.
