# File Research: sources/os/bsd/netbsd-src/sys/sys/timeb.h

Read completely: 59 lines.

Defines the deprecated `ftime(2)` ABI.

Key elements:
- `struct timeb` contains epoch seconds, milliseconds, timezone minutes west, and DST flag.
- Userland prototype declares `ftime(struct timeb *)`.

Risks and notes:
- Compatibility-only interface; new code should use modern time APIs.
- Layout remains ABI-sensitive for old binaries.
