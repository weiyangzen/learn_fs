# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_debug.h

Debug mask and logging macro header for ext4srv modules.

Key behavior:
- Defines one debug mask bit per subsystem, plus `DEBUG_NOPREFIX` and `DEBUG_ALL`.
- Maps debug mask IDs to subsystem prefixes via `ext4_dmask_id2str`.
- Defines text prefixes for info/warn/error messages.
- Declares global debug mask set/clear/get functions.
- Defines `ext4_dbg`, which checks the mask, optionally emits function/subsystem prefix, and prints to file descriptor 2.

Notable dependencies:
- Uses Plan 9 `fprint` through `ext4_config.h`.
- Implemented by `ext4_debug.c`.

Research notes:
- `ext4_dmask_id2str` handles single-bit masks; combined masks get no subsystem prefix.
- Debug output is process-global and not synchronized.
