# sources/storage-engines/pebble/replay/sampled_metric_test.go

## Purpose
This file provides datadriven tests for `SampledMetric` bucketization and graph rendering.

## Important APIs, Types, and Functions
`TestSampledMetric` supports `init`, `values`, `plot`, and `plot-increasing-per-sec` commands. `init` parses value/duration lines into cumulative sample timestamps without relying on wall-clock time.

## Control Flow
Each datadriven command updates or reads a shared `SampledMetric`. `values` prints fixed-width bucket output with one decimal place. Plot commands parse width, height, and scale and return the raw ASCII graph.

## State and Persistence Behavior
State is test-local and reset by `init` by reusing the existing sample slice capacity. The testdata file is the persisted expected-output contract.

## Dependencies and Integration Points
The test uses `datadriven`, `crstrings.LinesSeq`, `require`, and Go duration parsing. It directly exercises `SampledMetric.Values`, `Plot`, and `PlotIncreasingPerSec`.

## Risks
Because graph output is textual, small changes to bucket selection or `asciigraph` behavior can cause large golden diffs. The tests construct samples manually and do not exercise `record`'s wall-clock behavior.

## Test Signals
The file is itself the primary signal that replay metric graphs stay stable and that increasing counters are turned into bucketed rates as intended.
