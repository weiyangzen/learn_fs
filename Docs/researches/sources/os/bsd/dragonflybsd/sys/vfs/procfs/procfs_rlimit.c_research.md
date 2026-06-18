# File Research: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_rlimit.c

This file implements `/proc/<pid>/rlimit`. `procfs_dorlimit()` accepts reads only and formats every resource limit as `name current maximum`, using `-1` for `RLIM_INFINITY`.

It uses `_RLIMIT_IDENT` to expose `rlimit_ident[]` from resource headers and writes the formatted buffer via `uiomove_frombuf()`.

Research notes: the fixed 512-byte buffer is described as conservative; adding many resource limit names would require checking this assumption.
