# sources/object-store/minio/cmd/site-replication-metrics_gen.go

## Purpose
Generated tinylib/msgp serialization code for site-replication metric structs declared in `site-replication-metrics.go`. It provides MessagePack encoding, decoding, marshaling, unmarshaling, skipping unknown fields, and size estimation for metrics persistence/transport paths.

## Important APIs, Types, And Functions
For each supported type, the generator emits `DecodeMsg`, `EncodeMsg`, `MarshalMsg`, `UnmarshalMsg`, and `Msgsize`. Covered types are `RStat`, `RTimedMetrics`, `SRMetric`, `SRMetricsSummary`, `SRStats`, and `SRStatus`.

`RStat` serializes `Count` and `Bytes`. `RTimedMetrics` serializes `LastHour`, `SinceUptime`, `LastMinute`, and `ErrCounts`. `SRMetric` serializes deployment ID, endpoint health, latency, replicated totals, and failure metrics, but not `XferStats`. `SRMetricsSummary` serializes active workers, replica totals, queue/proxy metrics, peer metric map, and uptime. `SRStats` serializes replica totals and the deployment status map. `SRStatus` serializes replicated totals, failures, latency, large/small transfer stats under compact `lt`/`st` keys, endpoint, and secure flag.

## Control Flow
Decode paths read a map header, switch on field names, decode known fields, and skip unknown fields. Map fields are allocated or cleared before filling to avoid stale entries. Pointer fields such as `*SRStatus`, `XferRateLrg`, and `XferRateSml` handle nil values explicitly. Encode/marshal paths write fixed map sizes and field keys in generated order. `Msgsize()` returns an upper-bound estimate used for buffer preallocation.

## State And Persistence
The file performs no storage I/O itself, but defines the binary wire/storage shape for these metric types. Deserialization mutates receiver structs and clears existing maps. Unknown fields are skipped, giving some forward/backward compatibility.

## Dependencies And Integration Points
Depends on `github.com/tinylib/msgp/msgp` and msgp implementations for nested MinIO types such as replication windows, latency, transfer stats, active workers, queue/proxy metrics, and `madmin` latency/timed stats. It is regenerated from `//go:generate msgp -file $GOFILE` in the hand-written metrics file.

## Risks And Edge Cases
Because this file is generated, manual edits would be fragile. Wire field names are a compatibility surface; renaming struct fields or msg tags changes persisted/transported data. `SRMetric` serialization does not include `XferStats`, so consumers relying on msgp round trips should not expect the transfer summary map to survive for that DTO. Map iteration order is nondeterministic for encoded maps, which should be acceptable for MessagePack semantics but not byte-for-byte fixtures.

## Test Signals
`site-replication-metrics_gen_test.go` exercises marshal/unmarshal, skip, encode/decode, size warning, and benchmarks for every generated type. These tests validate codec mechanics, not semantic correctness of metric aggregation.
