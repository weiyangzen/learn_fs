# File Research: sources/os/plan9/9front/sys/src/cmd/cfs/file.c

Sparse file-data cache operations for `cfs`.

Key behavior:
- `fmerge` merges newly cached data into a block’s valid byte range.
- `fbwrite` writes one partial/full file block into the cache, allocating data blocks and converting direct pointers to indirect pointer blocks as needed.
- Write ordering marks data block, indirect block, and inode updates carefully.
- `fwrite` splits arbitrary byte writes across cache blocks.
- `fpget` locates the cached `Dptr` containing or following a requested file offset.
- `fread` reads cached bytes, returning positive bytes read, `0` for no data, or negative gap length when the requested offset starts in a cache hole.

Dependencies:
- Includes on-disk format, block cache, disk, inode, and file headers.

Research notes:
- The sparse range semantics are central to `cfs` fetching only gaps from the server.
