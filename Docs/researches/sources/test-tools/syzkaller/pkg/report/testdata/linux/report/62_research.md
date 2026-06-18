# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/62

## Purpose
This small fixture is another corrupted RCU stall sample. It expects the same hang title and alternate as report 61.

## Important APIs, types, and functions
The only useful raw line is `INFO: rcu_sched self-detected stall on CPU`; no reliable function stack is available.

## Control flow
The parser sees the RCU stall signature without enough stack detail and should produce a corrupted hang classification.

## State and persistence behavior
`CORRUPTED: Y` is the persisted expected state. The raw log is intentionally too short for normal attribution.

## Dependencies and integration points
It exercises duplicate/minimal corrupted hang handling in syzkaller's Linux report tests.

## Risks and test signals
The parser must not infer a random function name. Passing behavior keeps `TITLE: INFO: rcu detected stall in corrupted`.
