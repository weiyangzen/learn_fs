# File Research: sources/teaching/xv6-public/buf.h

Defines the in-memory disk block buffer.

Fields include:
- State flags, device number, block number, sleeplock, and reference count.
- LRU/MRU list links `prev`/`next`.
- Disk queue link `qnext`.
- `data[BSIZE]` block contents.

Defines buffer flags:
- `B_VALID`: data has been read from disk.
- `B_DIRTY`: data has been modified and needs writeback/log commit.
