# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_strdl.c

Default stream-based readline implementation.

Key behavior:
- `gp_readline_init` returns success without allocating state.
- `gp_readline` delegates directly to `sreadline`.
- `gp_readline_finit` is a no-op.

Notable dependencies:
- Stream readline API from `srdline.h` through `gp.h`.

Research notes:
- This is the fallback implementation when no enhanced platform readline package is used.
