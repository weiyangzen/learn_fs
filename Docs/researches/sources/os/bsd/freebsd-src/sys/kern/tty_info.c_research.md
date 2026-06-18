# File Research: sources/os/bsd/freebsd-src/sys/kern/tty_info.c

## Purpose
Implements tty status reporting for SIGINFO/`TIOCSTAT`, printing load average and foreground process information to the terminal.

## Core Behavior
- `proc_compare()` selects the most interesting process in the foreground pgrp, preferring runnable processes, higher CPU use, non-zombies, then higher PID.
- `thread_compare()` selects the most interesting thread in that process, preferring runnable/high-CPU/noninterruptible work.
- `tty_info()` prints load, command, PID, thread state, elapsed time, user/system CPU time, percent CPU, and RSS.
- When compiled with `STACK`, optional `kern.tty_info_kstacks` controls whether compact/long kernel stacks are included.
- `sbuf_tty_drain()` writes status through `tty_putstrn()` or console output when KDB is active.

## Dependencies
Uses scheduler CPU accounting, process/thread locks, pgrp membership, rusage calculation, VM resident counts, sbuf, optional stack capture, and TTY output processing.

## Notes and Risks
- Selection is intentionally best-effort; process/thread state can become stale after locks are dropped.
- Output is skipped if `tty_checkoutq()` says the TTY lacks enough output space.
