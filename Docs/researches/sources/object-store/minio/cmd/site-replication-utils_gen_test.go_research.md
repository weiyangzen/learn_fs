# sources/object-store/minio/cmd/site-replication-utils_gen_test.go

## Purpose
Generated test and benchmark coverage for `SiteResyncStatus` MessagePack serialization.

## Important APIs, Types, And Functions
Defines `TestMarshalUnmarshalSiteResyncStatus`, `BenchmarkMarshalMsgSiteResyncStatus`, `BenchmarkAppendMsgSiteResyncStatus`, `BenchmarkUnmarshalSiteResyncStatus`, `TestEncodeDecodeSiteResyncStatus`, `BenchmarkEncodeSiteResyncStatus`, and `BenchmarkDecodeSiteResyncStatus`.

## Control Flow
The marshal/unmarshal test serializes a zero-value `SiteResyncStatus`, deserializes it, asserts no leftover bytes, and checks that `msgp.Skip()` consumes the encoded message. The encode/decode test writes to a buffer, compares actual encoded length to `Msgsize()` as a warning, decodes into a new value, and verifies skip through a `msgp.Reader`. Benchmarks measure marshal, append, unmarshal, encode, and decode paths.

## State And Persistence
No persistent state. Tests operate only on zero-value structs and local buffers.

## Dependencies And Integration Points
Depends on generated codec methods in `site-replication-utils_gen.go` and `github.com/tinylib/msgp/msgp`. The file is generated and should remain synchronized with the source struct and codec generator.

## Risks And Edge Cases
The generated tests do not cover non-empty bucket-status maps, embedded target resync fields, or compatibility with older persisted metadata. They also do not exercise `siteResyncMetrics` load/save behavior. Their role is codec smoke testing and benchmark baselining.

## Test Signals
Useful mechanical signal that the generated `SiteResyncStatus` codec can round-trip zero values, skip encoded data, and maintain reasonable `Msgsize()` estimates. Limited semantic coverage for actual resync status workflows.
