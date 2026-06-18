# File Research: sources/os/bsd/openbsd-src/sys/sys/_types.h

Purpose: Defines internal fixed-width-derived base system types.

Key contents:
- Pulls machine-specific integer base types from `<machine/_types.h>`.
- Defines internal aliases for block counts/sizes, clocks, CPU IDs, device IDs, filesystem counts, gids, ids, network addresses/ports, inode numbers, IPC keys, modes, link counts, offsets, pids, resource limits, socket lengths, times, timers, uids, and microseconds.
- Defines opaque `__mbstate_t` as a 128-byte union aligned by `__int64_t`.

Filesystem relevance:
- Supplies base types such as `__dev_t`, `__ino_t`, `__mode_t`, `__nlink_t`, `__off_t`, `__fsblkcnt_t`, and `__fsfilcnt_t` used throughout VFS and public stat interfaces.
