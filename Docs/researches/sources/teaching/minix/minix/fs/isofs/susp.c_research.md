# File Research: sources/teaching/minix/minix/fs/isofs/susp.c

This file implements System Use Sharing Protocol parsing for isofs when Rock Ridge support is compiled in.

Key functions:
- `parse_susp(dir, buffer)`: handles fundamental SUSP entries.
- `parse_susp_buffer(dir, buffer, size)`: iterates SUSP entries and dispatches to fundamental SUSP or Rock Ridge parser.

Supported SUSP entries:
- `CE`: continuation area; recursively parses continuation data from another block.
- `PD`: padding.
- `SP`, `ER`, `ES`: ignored.
- `ST`: terminator; stops processing with `ECANCELED`.

Important behavior:
- Continuation parsing is limited to one logical block and comments note missing infinite-recursion protection.
- Rock Ridge parsing is skipped when `opt.norock` is true.
- Invalid entry length, zero signature, or too-small entries terminate parsing.

Role:
- Provides the generic extension entry walker used by `read_inode_susp()`.
