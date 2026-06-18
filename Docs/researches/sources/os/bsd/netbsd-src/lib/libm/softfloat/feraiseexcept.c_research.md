# File Research: sources/os/bsd/netbsd-src/lib/libm/softfloat/feraiseexcept.c

Implements `feraiseexcept`.

Key behavior:
- Sets requested sticky exception bits.
- Intersects requested exceptions with the enabled exception mask.
- If any enabled exception remains, builds a `siginfo_t` for `SIGFPE`.
- Chooses one `si_code` in priority order: underflow, overflow, divide-by-zero, invalid, inexact.
- Delivers the signal to the current process with `sigqueueinfo`.
- Always returns 0.

Notable detail:
- Includes `<stdio.h>` although the file does not use it.
