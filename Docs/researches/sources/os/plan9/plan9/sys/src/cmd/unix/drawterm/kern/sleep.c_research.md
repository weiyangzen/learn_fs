# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/sleep.c

This file duplicates the `Rendez` sleep/wakeup implementation also present in `rendez.c`.

Key behavior:
- `sleep` queues the current process on a `Rendez` until a predicate becomes true.
- `wakeup` removes and wakes one waiter.

Important details:
- Uses the same lock, `Proc.rnext`, `procsleep`, and `procwakeup` protocol as `rendez.c`.
- Build selection determines whether this or `rendez.c` supplies the symbols.
