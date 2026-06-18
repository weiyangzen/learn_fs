# sources/object-store/minio/cmd/erasure-server-pool-decom_gen_test.go

## Purpose
This generated test file verifies tinylib/msgp serialization scaffolding for decommission-related types. It also provides benchmarks for marshal, append-style marshal, unmarshal, streaming encode, and streaming decode.

## Important APIs, Types, and Functions
The file tests `PoolDecommissionInfo`, `PoolStatus`, `decomError`, `poolMeta`, and `poolSpaceInfo`. Each type has the same generated pattern: `TestMarshalUnmarshal...`, `BenchmarkMarshalMsg...`, `BenchmarkAppendMsg...`, `BenchmarkUnmarshal...`, `TestEncodeDecode...`, `BenchmarkEncode...`, and `BenchmarkDecode...`.

The tests use `bytes.Buffer`, `testing`, and `github.com/tinylib/msgp/msgp`. Benchmarks use `b.ReportAllocs`, `b.SetBytes`, `msgp.Nowhere`, and `msgp.NewEndlessReader`.

## Control Flow and State Behavior
Marshal/unmarshal tests create a zero-value instance, call `MarshalMsg(nil)`, call `UnmarshalMsg`, fail if an error occurs, and assert that no bytes are left over. They then call `msgp.Skip` on the encoded bytes and again assert full consumption.

Encode/decode tests encode a zero value to a buffer, compare the encoded length to `Msgsize` only as a warning, decode into a new zero value, and verify reader skip on the encoded buffer.

The tests exercise only in-memory serialization. They do not create `pool.bin`, do not validate the 4 byte `pool.bin` header, and do not verify compatibility with historical persisted data.

## Dependencies, Risks, and Test Signals
These tests integrate with `erasure-server-pool-decom_gen.go`; they do not call the handwritten decommission state machine. All tested values are zero values, leaving populated arrays, non-nil nested `PoolStatus.Decommission`, non-empty `CmdLine`, timestamps, and counters untested. Semantic coverage for `poolMeta.validate` lives in `erasure-server-pool-decom_test.go`.
