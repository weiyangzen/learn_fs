# File Research: sources/teaching/xv6-public/types.h

Read completely: 4 lines, 110 bytes.

Defines basic xv6 integer aliases: `uint`, `ushort`, `uchar`, and `pde_t`. Shared by kernel and user code.

Risk: assumes 32-bit `unsigned int` for `uint` and page directory entries.
