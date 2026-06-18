# sources/object-store/minio/cmd/bucket-stats_gen_test.go

## Purpose
This generated test file verifies tinylib/msgp generated serialization methods for replication stats types. It is mechanical coverage for binary round trips, skip behavior, allocation/performance benchmarks, and `Msgsize` estimate sanity.

## Important APIs, types, and functions
For each generated type, the file includes `TestMarshalUnmarshal<Type>`, `TestEncodeDecode<Type>`, and benchmarks for `MarshalMsg`, append-style `MarshalMsg`, `UnmarshalMsg`, `EncodeMsg`, and `DecodeMsg`. Covered types are `BucketReplicationStat`, `BucketReplicationStats`, `BucketStats`, `BucketStatsMap`, `ReplQNodeStats`, `ReplicationLastHour`, `ReplicationLastMinute`, `ReplicationLatency`, and `ReplicationQueueStats`.

## Control flow
Each marshal/unmarshal test creates a zero-value instance, marshals it, unmarshals it, asserts no leftover bytes, and verifies `msgp.Skip` consumes the encoded value. Each encode/decode test stream-encodes into a `bytes.Buffer`, warns if the buffer exceeds `Msgsize`, decodes with `msgp.Decode`, then verifies stream skip. Benchmarks repeatedly execute the same generated paths with allocation reporting and byte counts.

## State and persistence behavior
The tests are stateless and in-memory. They represent the persistence contract indirectly: if generated methods cannot encode, decode, unmarshal, or skip their own zero-value payloads, persisted replication stats and binary exchanges would fail.

## Dependencies and integration points
The file depends on `bytes`, `testing`, and `github.com/tinylib/msgp/msgp`. It integrates directly with generated methods in `bucket-stats_gen.go` and all nested msgp-enabled fields in the stats graph.

## Risks and test signals
The tests use zero values, so they do not exercise populated maps, slices, nested transfer stats, nil versus non-nil pointers, non-empty timestamps, fixed 60-slot values, unknown fields, or malformed payloads. Passing tests indicate generated method consistency and provide benchmark baselines, but they are not semantic tests for replication metrics.
