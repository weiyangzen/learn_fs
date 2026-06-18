# File Research: sources/local-fs/jfsutils/fsck/fsckruns.c

## Role

`fsckruns.c` implements the fsck heartbeat display. It installs a `SIGALRM` handler that periodically prints rotating heartbeat messages while fsck runs, then can restore the default alarm handler.

## Functions

- `fsck_hbeat(int unused)`:
  - Signal handler for `SIGALRM`.
  - Maintains a static volatile `current_heartbeat` index.
  - Prints heartbeat messages `fsck_HEARTBEAT0` through `fsck_HEARTBEAT8`, then back down through `fsck_HEARTBEAT1`, creating a back-and-forth animation.
  - Flushes stdout.
  - Rearms `alarm(1)`.

- `fsck_hbeat_start(void)`:
  - Initializes a `sigaction`.
  - Sets `sa.sa_handler = &fsck_hbeat`.
  - Uses `SA_RESTART`.
  - Installs the handler for `SIGALRM`.
  - Starts the one-second alarm.

- `fsck_hbeat_stop(void)`:
  - Restores `SIGALRM` handler to `SIG_DFL`.
  - Cancels pending alarms with `alarm(0)`.

## Dependencies

- Includes `signal.h`, `string.h`, `unistd.h`, and `xfsckint.h`.
- Uses `msg_defs[fsck_HEARTBEAT*].msg_txt` for displayed text.
- Declares `extern char *MsgText[]`, though this file uses `msg_defs` directly rather than `MsgText`.

## Notable Behavior

The source comment explicitly says the heartbeat handler is racy and the implementation accepts that. From a strict POSIX signal-safety standpoint, calling `printf()` and `fflush()` inside a signal handler is not async-signal-safe. In this utility context the handler is only for progress display, and the code prioritizes simple status output over signal-handler purity.

## Operational Impact

This file does not affect filesystem repair logic or disk state. Its side effects are limited to:

- Installing/restoring the process alarm handler.
- Printing heartbeat status to stdout.
- Scheduling/canceling periodic alarms.
