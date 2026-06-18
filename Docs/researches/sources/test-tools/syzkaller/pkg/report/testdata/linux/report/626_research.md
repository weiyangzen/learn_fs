# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/626

## Purpose
This fixture validates a panicking KMSAN uninitialized-value report in `prepare_task_switch`.

## Important APIs, types, and functions
Important frames include `prepare_task_switch`, `__schedule`, `__cond_resched`, `__dentry_kill`, `dentry_kill`, plus KMSAN reporting helpers. The metadata expects `TYPE: KMSAN-UNINIT-VALUE` and `PANICKED: Y`.

## Control flow
The scheduler prepares a task switch while a dentry release path is active, KMSAN reports use of uninitialized data, and the kernel panics.

## State and persistence behavior
The fixture persists sanitizer state, origin context, and panic classification. It has no mutable fixture state.

## Dependencies and integration points
It exercises KMSAN title extraction, scheduler frame selection, and panic suffix parsing.

## Risks and test signals
The parser must choose `prepare_task_switch` over surrounding VFS cleanup frames and keep the KMSAN type.
