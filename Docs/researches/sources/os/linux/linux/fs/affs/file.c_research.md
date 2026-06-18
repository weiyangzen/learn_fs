# File Research: sources/os/linux/linux/fs/affs/file.c

Purpose: implements AFFS regular file operations, block mapping, page-cache address-space operations, OFS-specific data-block handling, truncation, and fsync.

Key interfaces:
- `affs_file_operations`: generic file read/write/mmap/splice plus AFFS open/release/fsync.
- `affs_aops`: normal FFS buffered I/O, direct I/O, bmap, writepages.
- `affs_aops_ofs`: OFS-specific read/write path using data block headers.
- `affs_get_block()`: maps or allocates data blocks through AFFS extension blocks.
- `affs_truncate()` and `affs_free_prealloc()` manage file shrink/grow and preallocation cleanup.

Implementation notes:
- File open/release tracks `i_opencnt`; final close truncates to `mmu_private` and frees preallocations.
- Extension blocks are cached using a last-extension buffer, a linear cache, and a small associative cache to avoid repeated chain walks.
- `affs_alloc_extblock()` creates `T_LIST` extension blocks and links them through the previous block’s `extension` field.
- `affs_get_block()` maps logical blocks by extension index and block index within the extension table, allocating blocks only for append-at-end writes.
- Normal FFS uses block helpers (`block_read_full_folio`, `mpage_writepages`, `cont_write_begin`, `generic_write_end`).
- Direct I/O refuses extending writes by returning `0` when the write would pass `mmu_private`.
- OFS data blocks have 24-byte headers, data size fields, sequence numbers, and `next` links; OFS read/write paths copy payloads around those headers.
- Writes clear the Amiga archived bit (`FIBF_ARCHIVED`) and mark the inode dirty.

Dependencies:
- Uses AFFS allocation/free helpers, checksums, metadata buffer tracking (`mmb_*`), block buffer helpers, page-cache/blockdev helpers.

Edge cases:
- Logical block requests beyond allowed append position are treated as filesystem errors.
- OFS extension-to-hole writes call `affs_extent_file_ofs()` to materialize zeroed data blocks.
- Truncate frees data blocks and extension blocks after the new EOF and trims extension caches.
- Enlarging truncate uses the active mapping write path to force allocation/accounting.
