# File Research: sources/local-fs/xfsprogs/db/debug.h

Purpose: public debug state definitions.

Key contents:
- Defines `DEBUG_FLIST` as bit `0x1`.
- Declares global `debug_state`.
- Declares `debug_init(void)`.

Interactions:
- Included by `debug.c` and `flist.c`.

Risks/notes:
- Only one debug bit is defined in this header.
