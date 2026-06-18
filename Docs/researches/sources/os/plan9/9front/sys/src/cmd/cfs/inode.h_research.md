# File Research: sources/os/plan9/9front/sys/src/cmd/cfs/inode.h

Inode cache structures and declarations for `cfs`.

Key definitions:
- `Nicache` is 64 cached inodes.
- `Ibuf` embeds `Lru`, in-use flag, inode number, and on-disk `Inode` contents.
- `Imap` records whether a qid map entry is in use, the qid, and any resident `Ibuf`.
- `Icache` embeds `Disk`, stores inode count/layout constants, map pointer, inode buffer array, and LRU heads.
- Declares initialization, formatting, lookup, read/write, update, remove, and version-increment operations.

Dependencies:
- Requires `Disk`, `Inode`, `Qid`, and `Lru`.

Research notes:
- Like `Disk`, `Icache` uses struct embedding to layer inode management over disk allocation and block cache.
