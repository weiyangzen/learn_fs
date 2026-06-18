# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/save_nothing.c

`ipmon` discard saver backend.

Key behavior:
- Registers `nothingsaver`.
- Parses by allocating a tiny dummy context.
- `nothing_send()` deliberately ignores messages.

Research notes:
- `nothing_opts_t` is defined but unused.
