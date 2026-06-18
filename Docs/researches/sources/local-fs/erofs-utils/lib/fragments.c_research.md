# File Research: sources/local-fs/erofs-utils/lib/fragments.c

## Purpose
Implements EROFS packed-fragment support: tail-fragment dedupe, fragment packing, packed inode temp storage, packed inode flushing, lazy packed-file reading, and cache management.

## Main Structures
- `struct erofs_fragmentitem`: fragment data, length, and packed-file position.
- `struct erofs_fragment_bucket`: hash list plus rwsem.
- `struct erofs_packed_inode`: temp fd, hash buckets for mkfs, lazy-read bitmap, mutex, and bitmap size.

## Important Functions
- `z_erofs_fragments_tofh()`: computes tail hash from the last 64 bytes.
- `erofs_fragment_findmatch()`: searches fragment buckets for matching tail data and records matched fragment size/item.
- `erofs_fragment_pack()`: records a fragment in memory or as a reference to packed temp-file position.
- `erofs_pack_file_from_fd()`: appends an entire file to the packed temp inode, using mmap or sendfile/read fallback.
- `erofs_fragment_commit()`: writes in-memory fragment data to packed temp file and finalizes `inode->fragmentoff`.
- `erofs_flush_packed_inode()`: converts accumulated packed data into the special packed inode.
- `erofs_packedfile_init()` / `erofs_packedfile_exit()`: allocate/free packed inode state.
- `erofs_packedfile_read()`: reads from packed inode, using temp-file cache when initialized and falling back to on-disk packed inode reads.
- `erofs_packedfile_preload()`: lazily loads packed inode blocks into the temp fd and marks `uptodate` bits.

## Interactions
- Compression uses this for fragment tail packing and dedupe.
- Fsck initializes packed-file state to verify packed fragments.
- `data.c` calls `erofs_packedfile_read()` for fragment-backed compressed extents.

## Notes
The packed-file read path supports incremental/lazy loading of existing packed inodes and handles ENOSPC by clearing cache state and falling back.
