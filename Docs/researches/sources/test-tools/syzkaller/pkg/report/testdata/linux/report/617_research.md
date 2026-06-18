# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/617

## Purpose
This fixture covers an early boot denial-of-service style panic: `kernel panic: VFS: Unable to mount root fs on unknown-block(NUM,NUM)`.

## Important APIs, types, and functions
Important frames include `panic`, `mount_block_root`, `mount_root`, and `prepare_namespace`. The metadata sets `TYPE: DoS` and `PANICKED: Y`.

## Control flow
PID 1 reaches root filesystem mounting during namespace preparation and panics because the root block device cannot be resolved.

## State and persistence behavior
The file records boot-time global system state rather than per-process state. There is no recovery path in the fixture; the expected state is a panic.

## Dependencies and integration points
It integrates parser handling for early boot VFS panics where standard task stacks are short and no syzkaller executor is involved.

## Risks and test signals
The parser must normalize numeric block identifiers to `NUM,NUM` and classify the report as `DoS`, not as a generic panic.
