# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/porttime.c

This file provides local time formatting and dump scheduling helpers.

Key behavior:
- Implements simplified `kgmtime` and `klocaltime`.
- Uses a hardcoded timezone of 5 hours west of Greenwich with DST rules from `daytab`.
- `datestr` formats a timestamp as `YYYYMMDD`.
- `Tfmt` formats timestamps for KFS custom `%T` output, returning `"The Epoch"` for zero.
- `nextime` computes the next timestamp at a requested hour, skipping days represented by a bitmask.

Dependencies:
- Uses `Tm` from Plan 9 libc headers.
- `Tfmt` is registered by `formatinit`.

Notable detail:
- Leap-year logic is simple `year % 4`, matching old Plan 9 assumptions rather than full Gregorian century rules.
