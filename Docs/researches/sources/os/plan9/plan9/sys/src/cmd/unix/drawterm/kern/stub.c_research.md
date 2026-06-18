# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/stub.c

This file supplies hosted-kernel stubs for Plan 9 kernel services that drawterm does not implement fully.

Key behavior:
- No-op or diagnostic stubs: `mallocsummary`, `setswapchan`, `splx`, `splhi`, `spllo`, `procdump`, `kickpager`, `todset`, `todsetfreq`, `todinit`, `hostdomainwrite`, `hostownerwrite`, `postnote`.
- `todget` returns host nanoseconds via `nsec`.
- `exhausted` calls `panic`.
- `fastticks` derives a fast tick value from `nsec`.

Important details:
- Interrupt priority routines are placeholders in hosted drawterm.
- `postnote` always reports failure, reflecting limited signal/note emulation.
