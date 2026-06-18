# sources/storage-engines/pebble/replay/sampled_metric.go

## Purpose
This file defines `SampledMetric`, a lightweight time-series helper used by replay metrics to record sampled values and render summaries or ASCII graphs over replay time.

## Important APIs, Types, and Functions
`SampledMetric` stores `samples []sample` and the first sample time. `sample` records elapsed duration and int64 value.

`record` lazily initializes the first timestamp and appends an elapsed-time sample.

`Plot` buckets values through `Values`, scales them, and renders with `asciigraph`.

`PlotIncreasingPerSec` converts monotonically increasing counter samples into per-second bucket deltas before rendering.

`Mean`, `Min`, and `Max` compute simple aggregate statistics. `Values` and internal `values` project irregular samples into a fixed number of equally spaced time buckets.

## Control Flow
Samples are appended in observation order. Bucket projection computes the total duration from the last sample, divides it by the requested bucket count, and writes the latest sample value into the corresponding bucket, filling gaps with the next observed value.

## State and Persistence Behavior
The type is in-memory only. It keeps no locks and assumes single-threaded or externally synchronized recording and reads. The first timestamp anchors all future sample durations.

## Dependencies and Integration Points
The only external rendering dependency is `github.com/guptarohit/asciigraph`. Replay metric formatting code consumes `SampledMetric` for graphs and aggregate benchmark fields.

## Risks
`values` divides by `bucketDur`, which is `totalDur / buckets`; if all samples have zero elapsed duration and buckets is positive, this can produce a zero duration and a division panic. Empty samples and nonpositive bucket counts return nil safely. `Min` returns `math.MaxInt64` for no samples, unlike `Mean` and `Max`, so callers should avoid interpreting an empty minimum as meaningful.

## Test Signals
The paired datadriven test covers bucket projection, scaling, plotting, and per-second increasing deltas with synthetic durations.
