# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/646

## Purpose
This fixture validates a KASAN use-after-free read attributed to `tty_release`.

## Important APIs, types, and functions
Important frames include `__wake_up_common`, `tty_release`, KASAN report helpers, allocation stack from a syzkaller task, and free stack from a worker or async task.

## Control flow
TTY release uses a wait queue or related object after it has been freed. The top access helper is wakeup code, but the owning lifecycle path is `tty_release`.

## State and persistence behavior
The raw log persists allocation/free evidence, task IDs, memory state, and read classification.

## Dependencies and integration points
It tests KASAN use-after-free read parsing in TTY teardown and wakeup paths.

## Risks and test signals
The parser must pick `tty_release` over `__wake_up_common` and classify `TYPE: KASAN-USE-AFTER-FREE-READ`.
