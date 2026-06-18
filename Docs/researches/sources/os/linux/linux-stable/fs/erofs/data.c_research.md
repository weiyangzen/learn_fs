# File Research: sources/os/linux/linux-stable/fs/erofs/data.c

## Summary
Implements EROFS metadata buffering, logical block mapping, device mapping, uncompressed file I/O, iomap operations, DAX mapping, and file operations.

## Main Responsibilities
- Reads metadata from block, file-backed, fscache, or metabox mappings.
- Maps flat, inline, and chunk-based inode data.
- Resolves multi-device mappings.
- Tracks online folio completion for multipart reads.
- Implements iomap read, readahead, fiemap, bmap, direct I/O, and DAX mmap.

## Key APIs
- `erofs_read_metabuf()`
- `erofs_map_blocks()`
- `erofs_map_dev()`
- `erofs_fiemap()`
- `erofs_file_fops`

## Important Behavior
Flat files map to `startblk`; inline tail data maps to metadata. Chunk-based files read chunk indexes or block arrays. File-backed metadata avoids double caching by using the backing file mapping after range verification.

## Risks
Inline data must not cross a filesystem block. Device selection depends on device IDs, flat-device mode, and unified address ranges.
