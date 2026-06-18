# sources/object-store/minio/cmd/bucket-stats_gen.go

## Purpose
This generated file implements tinylib/msgp serialization for the replication statistics types declared in `bucket-stats.go`. It provides fast binary `DecodeMsg`, `EncodeMsg`, `MarshalMsg`, `UnmarshalMsg`, and `Msgsize` methods used for persistence, cached admin responses, or internal binary transport.

## Important APIs, types, and functions
The generated methods cover `BucketReplicationStat`, `BucketReplicationStats`, `BucketStats`, `BucketStatsMap`, `RMetricName`, `ReplQNodeStats`, `ReplicationLastHour`, `ReplicationLastMinute`, `ReplicationLatency`, and `ReplicationQueueStats`. The schema includes per-target fields like `ReplicatedSize`, `ReplicaSize`, `FailStats`, `Failed`, `Latency.UploadHistogram`, bandwidth fields, short keys `lt`/`st` for transfer rates, and deprecated pending/failed counters. Node queue stats serialize `NodeName`, `Uptime`, `ActiveWorkers`, `QStats`, and `MRFStats`.

## Control flow
Each decoder reads a map header, switches on field keys, decodes known fields, and skips unknown fields. Byte-slice unmarshal mirrors stream decode and returns leftovers. Encoders write fixed map headers and fields in generated order. Pointer fields such as `XferRateLrg` and `XferRateSml` support nil values. Maps and slices allocate or reuse capacity. `ReplicationLastHour` requires the encoded `Totals` array to have exactly 60 elements.

## State and persistence behavior
The generated key names and map sizes are a binary compatibility contract. Unknown-field skipping provides some forward compatibility, while encode paths emit only the fields known at generation time. `Msgsize` gives upper-bound estimates for preallocation and test warnings.

## Dependencies and integration points
The file depends on `github.com/tinylib/msgp/msgp` and nested msgp methods on `RTimedMetrics`, `TimedErrStats`, `LastMinuteHistogram`, `lastMinuteLatency`, `AccElem`, `ActiveWorkerStat`, `InQueueMetric`, `ReplicationMRFStats`, `ProxyMetric`, and `XferStats`. It must be regenerated when msgp-relevant stats structures change.

## Risks and test signals
Manual edits are unsafe because generation will overwrite them. Schema drift is the central risk; fields added to `bucket-stats.go` are not serialized until regeneration. Fixed array length protects `ReplicationLastHour` integrity but rejects malformed or incompatible payloads. Generated tests cover zero-value round trips, skip, stream encode/decode, and benchmarks, but not populated semantic payloads or backward compatibility.
