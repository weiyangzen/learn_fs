# sources/storage-engines/wiredtiger/test/suite/test_hs14.py

## Purpose

Performance regression test ensuring point-in-time reads with mostly invisible history-store records are not an order of magnitude slower than reads where HS records are visible.

## Important APIs, Types, and Functions

Defines `test_hs14`, `create_key`, and one workload across column and string row formats. It uses wall-clock `time.time`.

## Control Flow

It writes multiple versions per key, checkpoints to populate HS, measures scanning at read timestamp 3 where value3 is visible, then deletes at timestamp 5 and reinserts at 10, checkpoints again, and measures reads at timestamp 9 where keys are not found because HS entries are invisible.

## State and Persistence Behavior

State is a large HS population with visible and invisible windows. The persistence effect is checkpointed HS content; the metric is scan latency.

## Dependencies and Integration Points

Depends on timestamped transactions, checkpoints, `wiredtiger.WT_NOTFOUND`, and wall-clock timing.

## Risks and Maintenance Signals

Wall-clock tests can be noisy; the threshold is deliberately loose at 10x. It detects gross regressions rather than small performance changes.

## Test Signals

Signal is `invisible_hs_latency < visible_hs_latency * 10` with correct value/notfound assertions during scans.
