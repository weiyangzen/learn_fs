# File Research: sources/local-fs/erofs-utils/lib/data.c

## Purpose
Read-side data and metadata mapping for EROFS inodes, including raw files, inline data, chunk-based files, compressed files, packed fragments, metabox metadata, and variable-sized metadata records.

## Important Functions
- `erofs_bread()`: reads a metadata block into an `erofs_buf`, optionally from metabox inode when no direct vfile is set.
- `erofs_init_metabuf()` / `erofs_read_metabuf()`: initialize/read metadata buffers.
- `__erofs_map_blocks()`: maps non-compressed flat/inline/chunk-based extents.
- `erofs_map_blocks()`: dispatches to compressed zmap for compressed inodes, otherwise raw mapping.
- `erofs_map_dev()`: resolves multi-device physical offsets.
- `erofs_read_one_data()`: reads mapped raw data from the proper device.
- `erofs_read_raw_data()`: reads arbitrary raw inode data, filling holes with zeros and handling inline metabox data.
- `z_erofs_read_one_data()`: reads and decompresses one compressed extent or packed fragment.
- `z_erofs_read_data()`: backward extent iteration for compressed reads over arbitrary ranges.
- `erofs_preadi()` / `erofs_iopen()`: expose an inode as `struct erofs_vfile`.
- `erofs_read_metadata()`: reads length-prefixed metadata either from an inode or block-device metadata area.

## Interactions
- Used by fsck, directory iteration, xattr reading, packed-file handling, and decompression.
- Calls `z_erofs_decompress()` from `decompress.c`.
- Uses packed-file reads from `fragments.c` for fragment-backed data.

## Notes
Inline data crossing a metadata block boundary is treated as corruption.
