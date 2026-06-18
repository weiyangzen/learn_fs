# sources/object-store/minio/cmd/last-minute.go

## Purpose

`last-minute.go` implements a compact rolling one-minute latency histogram split by object-size buckets. It is used to accumulate recent operation timing and byte counts and expose them as `madmin.TimedAction`-compatible counters.

## Important APIs, Types, Control Flow, And State

The size bucket constants classify objects into less than 1 KiB, 1 MiB, 10 MiB, 100 MiB, 1 GiB, and greater than 1 GiB. `sizeToTag` maps a byte size to an index; `sizeTagToString` returns stable diagnostic labels. `AccElem` stores accumulated duration in nanoseconds, total bytes, and count. Its `add` clamps negative durations to zero, `merge` combines totals, `avg` returns mean latency, and `asTimedAction` converts to madmin's wire type.

`lastMinuteLatency` stores 60 `AccElem` slots and `LastSec`. `add`, `addAll`, and `getTotal` call `forwardTo` before reading or writing so stale second slots are cleared. `forwardTo` clears the entire ring when the gap is at least 60 seconds, or advances one second at a time clearing overwritten slots. `LastMinuteHistogram` is an array of `lastMinuteLatency` indexed by size bucket; `Merge` aligns and merges two histograms, `Add` records an event, and `GetAvgData` returns the per-bucket one-minute totals.

State is entirely in memory, with generated MessagePack support in `last-minute_gen.go` for transport or persistence by callers. Dependencies are `time` and `madmin-go`.

## Risks And Test Signals

Risks include second-boundary behavior, wall-clock jumps, zero initialization where `LastSec` starts at zero, and callers forgetting to increment `AccElem.Size` before `addAll`/merge paths. The generated tests validate serialization shape, but this file lacks direct unit tests for bucket boundary classification, ring expiry, negative duration clamping, or merge alignment.
