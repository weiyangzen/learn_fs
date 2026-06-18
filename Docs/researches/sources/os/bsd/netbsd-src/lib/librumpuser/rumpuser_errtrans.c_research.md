# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_errtrans.c

## Summary
Translates host `errno` values into NetBSD/rump kernel errno numbers.

## Key Details
- Returns zero unchanged.
- Uses `#ifdef`-guarded switch cases so the same source builds on hosts with different errno macro sets.
- Maps common POSIX, networking, RPC, filesystem, authentication, message, STREAMS, and overflow errors to fixed rump errno numbers.
- Handles aliases such as `EWOULDBLOCK == EAGAIN` and `ENOTSUP == EOPNOTSUPP` without duplicate case labels.
- Defaults unknown host errors to rump `EINVAL` (`22`).

## Notes
The comment says the table was pseudo-automatically generated but is intended to be edited for duplicate errno values.
