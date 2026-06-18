# sources/storage-engines/wiredtiger/bench/wtperf/runners/update-btree.json

## Purpose
This JSON file defines three wtperf runner variants for update-btree-style workloads, each emphasizing a different operation by throttling the others.

## Important APIs, Types, and Functions
The file is an array of objects. Each object has `arguments`, a list containing a `-o threads=...` override, and `operations`, a list of metric names expected from the run.

## Control Flow
A runner harness reads each object, invokes wtperf with the listed thread override, and records the named operations. The first case leaves reads unthrottled and records read/load; the second leaves updates unthrottled; the third leaves inserts unthrottled.

## State and Persistence Behavior
No state is modified by the file itself. It defines benchmark matrix metadata consumed by external scripts.

## Dependencies and Integration Points
It depends on wtperf accepting `-o threads=((...))` syntax and on the runner interpreting `operations` names such as `read`, `load`, `update`, and `insert`.

## Risks and Edge Cases
JSON is valid but shell-like argument strings require the consuming harness to preserve quoting. Operation names must match downstream parser expectations. Thread counts and throttle values are benchmark policy and can become stale as hardware changes.

## Test Signals
Run the consuming wtperf runner over this file and verify all three cases execute and produce the requested metrics.
