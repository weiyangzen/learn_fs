# sources/object-store/minio/cmd/erasure-server-pool-decom_gen.go

## Purpose
This generated file supplies tinylib/msgp encoders, decoders, marshalers, unmarshalers, and size estimators for decommission persistence and status types from `erasure-server-pool-decom.go`. It is the serialization layer used when `pool.bin` is read and written.

## Important APIs, Types, and Functions
The generated methods cover `PoolDecommissionInfo`, `PoolStatus`, `decomError`, `poolMeta`, and `poolSpaceInfo`. For each type, the generated surface is `DecodeMsg`, `EncodeMsg`, `MarshalMsg`, `UnmarshalMsg`, and `Msgsize`.

`PoolDecommissionInfo` encodes a 16-field map using compact msg keys: `st`, `ss`, `ts`, `cs`, `cmp`, `fl`, `cnl`, `bkts`, `dbkts`, `bkt`, `pfx`, `obj`, `id`, `idf`, `bd`, and `bf`. `PoolStatus` encodes `id`, `cl`, `lu`, and `dec`; `dec` supports nil and lazy allocation. `poolMeta` encodes `v` and `pls`.

## Control Flow
Decode paths read a map header, loop over keys, switch on `msgp.UnsafeString(field)`, decode known fields, and skip unknown fields. Array fields reuse capacity when possible and allocate when the incoming array is larger. Nested structures delegate to their own generated decode methods.

Encode and marshal paths write fixed map headers and fields in deterministic order. `MarshalMsg` grows the supplied byte slice with `msgp.Require` using `Msgsize` as an upper-bound estimate. Unmarshal byte-slice paths return the unused suffix in `o`.

## State and Persistence Behavior
This file does not choose when state is persisted; it defines the binary body that `poolMeta.save` stores after the 4 byte `pool.bin` header. Unknown fields are skipped, which gives some forward compatibility for additive schema changes. Missing fields decode to Go zero values.

Nil handling is significant for `PoolStatus.Decommission`: nil means no decommission state and therefore a pool is not suspended by `poolMeta.IsSuspended`; non-nil means decommission state exists.

## Dependencies, Risks, and Test Signals
The only direct external dependency is `github.com/tinylib/msgp/msgp`. Runtime integration is through `poolMeta.load` and `poolMeta.save`, and through generated tests in `erasure-server-pool-decom_gen_test.go`.

Manual edits would be overwritten. Schema key changes in struct tags would break compatibility with existing `pool.bin` unless migration handling is added. Generated tests verify zero-value round trips and skip behavior, but not populated queued buckets, nested decommission info, or non-empty command lines.
