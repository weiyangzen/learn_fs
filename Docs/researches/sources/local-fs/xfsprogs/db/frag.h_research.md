# File Research: sources/local-fs/xfsprogs/db/frag.h

Purpose: public declaration for fragmentation command initialization.

Key contents:
- Declares `frag_init(void)`.

Interactions:
- Included by `command.c`, which calls `frag_init`.

Risks/notes:
- Minimal single-function header.
