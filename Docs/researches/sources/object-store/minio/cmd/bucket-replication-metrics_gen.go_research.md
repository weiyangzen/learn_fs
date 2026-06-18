# sources/object-store/minio/cmd/bucket-replication-metrics_gen.go

Purpose: Generated `tinylib/msgp` codecs for metric structs declared in `bucket-replication-metrics.go`. It provides binary encode/decode, marshal/unmarshal, and size-estimation methods used when replication metrics are exchanged or persisted through msgp-compatible paths.

Important APIs/types: For `ActiveWorkerStat`, `InQueueMetric`, `InQueueStats`, `ProxyMetric`, `QStat`, `ReplicationMRFStats`, `SMA`, and `XferStats`, the file implements `DecodeMsg`, `EncodeMsg`, `MarshalMsg`, `UnmarshalMsg`, and `Msgsize`. Field keys use explicit `msg` tags where present (`cq`, `aq`, `pq`, `cr`, `av`, `p`, `n`, proxy counter abbreviations) and Go field names where no tag exists.

Control flow: Each `DecodeMsg`/`UnmarshalMsg` reads a map header, iterates keys, assigns known fields, and skips unknown fields. Nested structs such as `InQueueMetric` decode embedded `QStat`-shaped maps for current/average/max queue values. `MarshalMsg` preallocates using `Msgsize`, appends a map header and field keys, then appends primitive values. `EncodeMsg` streams the same structure to a `msgp.Writer`.

State and persistence: The generated code serializes only exported/tagged data fields. Runtime-only fields in metrics such as histograms, mutexes, `rateMeasurement`, and `SMA.buf/window/idx/prevSMA/filledBuf` are absent or unexported; this preserves the snapshot contract but does not reconstruct live collectors. `XferStats` serializes `Curr`, `Avg`, `Peak`, and `N`, not the moving-average machinery.

Dependencies and integration points: Depends only on `github.com/tinylib/msgp/msgp` and the metric types from package `cmd`. Regeneration is controlled by `//go:generate msgp -file $GOFILE` in the hand-written metrics file.

Risks: Manual edits would be overwritten and can desynchronize from struct tags. Adding/removing fields in the source structs requires regenerating this file and its tests. Because unknown fields are skipped, forward compatibility is tolerant, but missing live internals after decode can surprise code that treats decoded values as active collectors. Map iteration order is irrelevant for decode but can make binary output order for maps unstable where maps exist in other generated files.

Test signals: `bucket-replication-metrics_gen_test.go` contains round-trip encode/decode tests and benchmarks for every type covered here. It verifies no trailing bytes remain and that `msgp.Skip` can skip encoded values.
