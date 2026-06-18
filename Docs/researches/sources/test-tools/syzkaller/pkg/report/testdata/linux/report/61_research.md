# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/61

## Purpose
This very small fixture marks an RCU stall report as corrupted. It expects `TITLE: INFO: rcu detected stall in corrupted`, `ALT: stall in corrupted`, `TYPE: HANG`, and `CORRUPTED: Y`.

## Important APIs, types, and functions
The only raw log signal is `INFO: rcu_sched self-detected stall on CPU`. The important parser API behavior is not stack extraction but corruption-aware classification.

## Control flow
The metadata header precedes a minimal RCU stall line. There is not enough stack context to identify a trustworthy blocked function, so the expected function token is `corrupted`.

## State and persistence behavior
The fixture persists a negative-quality crash sample. `CORRUPTED: Y` is part of the expected state consumed by the report test harness.

## Dependencies and integration points
It integrates with syzkaller's RCU stall and hang recognizers and verifies that incomplete logs do not produce overconfident function names.

## Risks and test signals
The risk is false precision. Passing behavior preserves the corrupted marker, hang type, and alternate title instead of inventing a stack frame.
