# File Research: sources/teaching/pintos/src/filesys/inode.c

## Purpose
Implements Pintos inode storage. This is a deliberately simple extent-based inode layer: each file owns one contiguous run of sectors allocated at creation time, and files do not grow.

## Main Data Structures
- `struct inode_disk`
  - On-disk inode, exactly one block sector.
  - Fields:
    - `start`: first data sector.
    - `length`: file size in bytes.
    - `magic`: inode magic value.
    - `unused[125]`: padding/reserved.
- `struct inode`
  - In-memory inode.
  - Tracks open-list membership, inode sector, open count, removed flag, write-denial count, and cached on-disk inode data.

## Key Functions
- `bytes_to_sectors(size)`
  - Rounds byte length up to full sectors.
- `byte_to_sector(inode, pos)`
  - Maps a byte offset to `data.start + pos / BLOCK_SECTOR_SIZE`.
  - Returns `(block_sector_t)-1` if `pos` is outside file length.
- `inode_init()`
  - Initializes global open-inode list.
- `inode_create(sector, length)`
  - Allocates a contiguous data extent.
  - Writes the on-disk inode to `sector`.
  - Zero-fills allocated data sectors.
- `inode_open(sector)`
  - Reuses an already-open in-memory inode for the same sector.
  - Otherwise allocates, initializes, reads inode data, and adds it to `open_inodes`.
- `inode_reopen(inode)`
  - Increments open count.
- `inode_get_inumber(inode)`
  - Returns inode sector number.
- `inode_close(inode)`
  - Decrements open count.
  - On final close, removes from open list.
  - If marked removed, releases inode sector and data sectors.
- `inode_remove(inode)`
  - Marks an inode for deletion on final close.
- `inode_read_at(inode, buffer, size, offset)`
  - Reads possibly partial sectors using a bounce buffer when needed.
- `inode_write_at(inode, buffer, size, offset)`
  - Writes possibly partial sectors using a bounce buffer when needed.
  - Refuses writes when `deny_write_cnt > 0`.
  - Does not extend files.
- `inode_deny_write(inode)` / `inode_allow_write(inode)`
  - Maintain inode-level deny-write count.
- `inode_length(inode)`
  - Returns cached file length.

## Important Behavior
- On-disk inode size is asserted to equal `BLOCK_SECTOR_SIZE`.
- All file data sectors must be contiguous.
- File length is fixed at creation. Writes at or beyond EOF stop instead of allocating more sectors.
- The open-inode list ensures multiple opens of the same inode sector share one `struct inode`.
- The `removed` flag is in-memory only; deletion is completed when the final opener closes the inode.
- The comment on `inode_close()` says it writes the inode to disk, but the implementation does not write inode metadata on close. This is acceptable for the current fixed-size inode because mutable metadata is minimal and not persisted there.
- No synchronization is present around the open-inode list, open counts, or I/O paths.

## Dependencies
- Uses `filesys/free-map.h` for sector allocation/release.
- Uses `filesys/filesys.h` for `fs_device`.
- Uses block read/write primitives through included block APIs.
- Uses Pintos list utilities for open-inode deduplication.

## Research Notes
- This implementation is the core limitation behind several higher-level behaviors: no file growth, fixed directory capacity, contiguous allocation, and no indexed or indirect blocks.
