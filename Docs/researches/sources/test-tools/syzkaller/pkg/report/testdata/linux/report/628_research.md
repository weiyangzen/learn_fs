# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/628

## Purpose
This fixture validates an `ATOMIC_SLEEP` report where `console_lock` is called with interrupts disabled and TTY locks held.

## Important APIs, types, and functions
Important frames include `__might_resched`, `console_lock`, `do_con_write`, `con_write`, `n_hdlc_send_frames`, `tty_wakeup`, `__start_tty`, `n_tty_ioctl_helper`, `n_hdlc_tty_ioctl`, `tty_ioctl`, and `__x64_sys_ioctl`.

## Control flow
An ioctl on a TTY enters HDLC line-discipline handling, wakes the TTY, sends frames, attempts console output, and reaches a sleeping console lock in atomic context.

## State and persistence behavior
The log persists lock state, IRQ state, preempt count, and syscall registers. The fixture itself is immutable.

## Dependencies and integration points
It tests atomic-sleep parsing for TTY/console paths and held-lock context.

## Risks and test signals
The parser must preserve `console_lock` as the title frame and classify the report as `ATOMIC_SLEEP`.
