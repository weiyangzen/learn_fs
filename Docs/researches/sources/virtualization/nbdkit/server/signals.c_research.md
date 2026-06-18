# File Research: sources/virtualization/nbdkit/server/signals.c

This file installs process signal handlers. On POSIX it uses `sigaction` with `SA_RESTART` for `SIGINT`, `SIGQUIT`, `SIGTERM`, and `SIGHUP`, routing them to `handle_quit`. It also ignores `SIGPIPE` so socket write failures are handled as ordinary errors instead of terminating the process.

On Windows it installs `signal` handlers for `SIGINT` and `SIGTERM`. The file is intentionally small; actual shutdown state and wakeup mechanics live in `quit.c`.
