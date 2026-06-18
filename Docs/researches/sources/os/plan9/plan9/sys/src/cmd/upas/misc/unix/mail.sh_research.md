# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/misc/unix/mail.sh

## Purpose
Shell version of the Unix `/bin/mail` compatibility wrapper.

## Behavior
Dispatches `-n` to `LIBDIR/notify`, reader-style flags or empty invocation to `LIBDIR/edmail`, and all other invocations to `LIBDIR/send`.

## Dependencies
POSIX shell; install-time substitution of `LIBDIR`.

## Risks / Notes
Uses `$*`, so shell word preservation depends on caller/legacy expectations.
