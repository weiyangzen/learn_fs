# File Research: sources/os/bsd/netbsd-src/sys/sys/spldebug.h

Read completely: 41 lines.

This header declares SPL debugging hooks: `spldebug_start`, `spldebug_stop`, `spldebug_lower`, and `spldebug_raise`.

Risks: declaration-only. Use depends on the platform/debug implementation tracking interrupt-priority transitions consistently.
