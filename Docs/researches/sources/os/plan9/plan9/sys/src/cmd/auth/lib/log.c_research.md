# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/lib/log.c

Provides shared login-attempt logging helpers. `record` writes `bad` or `good` to a user’s `log` file in a key database.

`logfail` records failures for both Plan 9 and network key databases; `succeed` records successes for both; `fail` logs a failure and exits. These integrate with `keyfs` log counters.
