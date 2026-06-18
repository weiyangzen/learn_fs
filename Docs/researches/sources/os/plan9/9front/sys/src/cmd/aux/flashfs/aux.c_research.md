# File Research: sources/os/plan9/9front/sys/src/cmd/aux/flashfs/aux.c

Role: Allocation helpers for flashfs and older bundled 9P support.

Functions:
- `emalloc9p` allocates, zeroes, tags, and exits on failure.
- `erealloc9p` reallocates, tags, and exits on failure.
- `estrdup9p` duplicates strings, tags allocations, and exits on failure.

Integration:
- Shared by flashfs code for robust fail-fast allocation.
- Includes Plan 9 auth/fcall/thread and local `"9p.h"`, indicating this code originated around a bundled or compatibility 9P layer.
