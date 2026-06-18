# sources/object-store/minio/cmd/last-minute_gen.go

## Purpose

`last-minute_gen.go` is `tinylib/msgp` generated serialization code for the latency histogram types in `last-minute.go`. It provides MessagePack encode/decode, marshal/unmarshal, and size-estimation methods for `AccElem`, `LastMinuteHistogram`, and `lastMinuteLatency`.

## Important APIs, Control Flow, And State

For `AccElem`, the generated code serializes a three-field map containing `Total`, `Size`, and `N` as int64 values. For `lastMinuteLatency`, it serializes a two-field map containing `Totals`, a fixed array of 60 `AccElem` maps, and `LastSec`. For `LastMinuteHistogram`, it serializes a fixed array with `sizeLastElemMarker` elements, each in the same `lastMinuteLatency` map shape. Decode and unmarshal paths validate the fixed array lengths and return `msgp.ArrayError` on mismatch. Unknown map fields are skipped, which gives forward compatibility for added fields but not for changed array lengths.

This file has no business logic or persistent state beyond the binary wire representation it defines. It depends only on `github.com/tinylib/msgp/msgp` and the source types.

## Risks And Test Signals

The biggest risk is schema coupling to constants: changing `sizeLastElemMarker` or the 60-second ring shape makes existing serialized data incompatible unless migration is handled elsewhere. Because the file is generated, manual edits would be overwritten and should be avoided. `last-minute_gen_test.go` covers marshal/unmarshal, stream encode/decode, `Skip`, `Msgsize` upper-bound checks, and benchmarks for all three generated types, but it uses zero-value data only.
