# sources/storage-engines/wiredtiger/bench/wtperf/runners/update-checkpoint.json

## Purpose
This JSON file defines update/checkpoint benchmark variants analogous to `update-btree.json`, but with one insert thread in each thread mix, likely to pair update-heavy workloads with checkpoint-sensitive profiles.

## Important APIs, Types, and Functions
The schema is an array of objects with `arguments` and `operations`. Each argument is a wtperf `-o threads=...` override. Operation metric groups are `read`/`load`, `update`, and `insert`.

## Control Flow
An external runner iterates entries, passes the override to wtperf, and extracts requested metrics. Throttles shift the performance focus between reads, updates, and inserts.

## State and Persistence Behavior
The file has no direct runtime state. It configures benchmark invocations and expected metric extraction.

## Dependencies and Integration Points
It depends on wtperf option parsing and runner harness JSON support. It is part of the `bench/wtperf/runners` workload catalog.

## Risks and Edge Cases
As with other runner JSON, argument quoting and metric-name compatibility are the main fragility. The lower insert thread count compared with `update-btree.json` is intentional benchmark policy but should be documented in consuming dashboards to avoid miscomparison.

## Test Signals
Execute all entries through the benchmark harness and confirm metric files contain read/load, update, and insert outputs as declared.
