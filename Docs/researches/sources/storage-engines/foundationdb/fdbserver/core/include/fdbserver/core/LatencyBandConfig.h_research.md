# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/LatencyBandConfig.h

## Purpose
This header defines the serialized configuration for latency-band telemetry. It lets the system parse JSON configuration into request-specific latency buckets and optional request-size limits for GRV, read, and commit paths.

## Important APIs, Types, And Functions
`LatencyBandConfig` contains `GrvConfig`, `ReadConfig`, and `CommitConfig`. `RequestConfig` stores `std::set<double> bands`, implements JSON loading through `fromJson`, and supports equality via virtual `isEqual`. `ReadConfig` adds `maxReadBytes` and `maxKeySelectorOffset`; `CommitConfig` adds `maxCommitBytes`. `LatencyBandConfig::parse(ValueRef)` is the public parser.

## Control Flow
The parser consumes a configuration string, builds per-request subconfigs from JSON, and later serializes the result through `ServerDBInfo`. Equality checks delegate to subtype-specific fields so broadcasts can detect material changes.

## State And Persistence Behavior
The config is transient cluster metadata carried in `ServerDBInfo`; it is not persisted by this header. Serialization preserves bands and optional thresholds for cross-process propagation.

## Dependencies And Integration Points
It depends on FDB types and `JSONDoc`. `ServerDBInfo` includes `Optional<LatencyBandConfig>`, making it visible to workers and request-serving roles that emit latency metrics.

## Risks And Edge Cases
Invalid JSON, missing fields, negative/empty bands, and equality between base/subtype configs are the main risks. Optional thresholds must remain absent when unspecified so defaults are not confused with explicit zero limits.

## Test Signals
Useful tests parse representative JSON strings, round-trip serialization, compare equal and unequal configs, and confirm read/commit thresholds are applied only to their matching request classes.
