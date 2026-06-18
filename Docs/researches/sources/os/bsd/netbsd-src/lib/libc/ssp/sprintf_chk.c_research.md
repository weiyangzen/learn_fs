# File Research: sources/os/bsd/netbsd-src/lib/libc/ssp/sprintf_chk.c

Read completely: 63 lines.

This file implements `__sprintf_chk`. If the destination object size is representable as an `int`, it formats through `vsnprintf` using `slen` and fails when the formatted length would not fit; otherwise it falls back to `vsprintf`.

Important interactions: fortified `sprintf` backend.

Security/reliability notes: the large-object fallback preserves unbounded `sprintf` behavior, which is compatibility-oriented rather than strictly safe.
