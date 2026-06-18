# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/trace.c

Purpose: Provides named trace categories and HTML log trace emission.

Key behavior:
- Defines trace category strings for disk, lump, block, proc, work, quiet, and rpc.
- `trace` formats messages into category-specific and all-category `vtlog` streams when `ventilogging` is enabled.
- `traceinit` and `settrace` are stubs.

Dependencies:
- Uses `vtlog`, thread names, Venti time formatting, and global `ventilogging`.

Notable details:
- Runtime trace filtering is not implemented here; category strings are passed through to log destinations.
