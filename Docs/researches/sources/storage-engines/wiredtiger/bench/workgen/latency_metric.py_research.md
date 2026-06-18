# sources/storage-engines/wiredtiger/bench/workgen/latency_metric.py

## Purpose
This script computes latency summary metrics from workgen `monitor.json` files, especially comparing read latency during checkpoint intervals versus normal intervals.

## Important APIs, Types, and Functions
`Digest` accumulates entries, operations, weighted average latency, raw/weighted 99th percentile latency, max latency, and elapsed seconds. `Metric` stores report metadata. `FileMetrics` parses one file and calculates `Average latency reads us`, `Max latency reads us`, `Max vs average latency`, `Checkpoint vs normal 99%`, and `Proportion of ckpt time`. Helper functions format a table.

## Control Flow
The script parses argv for `--raw` and filenames. Each `FileMetrics.calculate` wraps JSON lines into a synthetic `{"ts": [...]}` array and calls `calculate_using_json`. Iteration tracks checkpoint active transitions, skips the first entry for elapsed-time calculation, splits read stats into checkpoint or normal digests, validates that there are entries/ops and at least two checkpoints, computes metrics, and prints a table across files. Raw mode dumps digest internals.

## State, Persistence, and Dependencies
State is in per-file metric/digest objects. Dependencies include `json`, `datetime`, monitor entries with `localTime`, `workgen.checkpoint.active`, and `workgen.read` latency fields.

## Integration Points, Risks, and Test Signals
It integrates with workgen runs that emit monitor JSON. Risks include loading entire files into memory, strict timestamp format, exceptions when checkpoint coverage is insufficient, and weighted/raw 99th percentile semantics that should be understood before thresholding. Signal is tabular output or detailed raw diagnostics.
