# sources/object-store/minio/cmd/site-replication-metrics_gen_test.go

## Purpose
Generated test and benchmark coverage for MessagePack serialization of site-replication metric types.

## Important APIs, Types, And Functions
For each generated metric type, the file emits a marshal/unmarshal test, encode/decode test, marshal/append/unmarshal benchmarks, and encode/decode benchmarks. Covered types are `RStat`, `RTimedMetrics`, `SRMetric`, `SRMetricsSummary`, `SRStats`, and `SRStatus`.

## Control Flow
Each marshal/unmarshal test creates a zero-value instance, calls `MarshalMsg(nil)`, calls `UnmarshalMsg()`, asserts no leftover bytes, and verifies `msgp.Skip()` consumes the whole message. Each encode/decode test encodes into a `bytes.Buffer`, logs a warning if `Msgsize()` is smaller than actual encoded size, decodes into a new value, then verifies reader `Skip()`.

## State And Persistence
No persistent state. All values are zero-value in-memory structs and local buffers. Benchmarks reuse local buffers or endless readers for allocation/throughput measurement.

## Dependencies And Integration Points
Depends on the generated codec methods in `site-replication-metrics_gen.go` and `github.com/tinylib/msgp/msgp`. These tests are generated alongside codec code and should be regenerated rather than manually edited.

## Risks And Edge Cases
Generated tests only cover zero-value structs, so they do not validate non-empty maps, nested pointer combinations, transfer stats content, or backwards compatibility with older field sets. They are still useful for catching broken generated methods, invalid size estimates, and basic decode/skip failures.

## Test Signals
Good mechanical codec smoke tests and allocation benchmarks. Limited semantic signal for replication metric correctness or production-like encoded data.
