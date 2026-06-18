# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/time.c

This file implements Plan 9 `time`.

Key behavior:
- `time` reads `/dev/time` and returns seconds.
- `oldtime` is a fallback/helper for older formatted time data.

Important details:
- Caches the time fd where possible.
- Distinct from host POSIX `time`.
