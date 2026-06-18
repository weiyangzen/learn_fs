# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/devwren.c

This file implements the normal single-file “wren” block device backend for KFS.

Key behavior:
- `wreninit` opens `wrenfile`, reads the first block, detects KFS magic and block size, records backing file size, and stores the fd.
- `wrenream` writes KFS magic and selected block size to the first block.
- `wrentag` checks the tag trailer at `BUFSIZE`.
- `wrencheck` validates magic, superblock tag, root directory tag, and root allocation.
- `wrensize` reports backing file size divided by `RBUFSIZE`.
- `wrensuper` returns block 1 and `wrenroot` returns block 2.
- `wrenread` and `wrenwrite` seek and transfer exactly one KFS raw block.

Dependencies:
- Uses KFS block sizing and tag layout.
- Device dispatch table in `dat.c` calls these functions for `Devwren`.

Notable details:
- Magic is stored at offset 256 in the first block as `"kfs wren device\n"` followed by block size.
- Read/write failures are printed and returned as nonzero status.
