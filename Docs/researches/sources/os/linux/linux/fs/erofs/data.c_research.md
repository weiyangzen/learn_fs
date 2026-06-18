# File Research: sources/os/linux/linux/fs/erofs/data.c

Implements EROFS metadata buffering, uncompressed block mapping, device mapping, online folio completion, iomap integration, and regular file operations.

Key behavior:
- `erofs_bread()` reads metadata folios from block device, fscache inode, file-backed mapping, or metabox mapping and optionally kmaps them.
- `erofs_init_metabuf()` selects the correct metadata mapping based on metabox, file-backed, fscache, or block-device mode.
- `erofs_map_blocks()` maps flat plain/inline data and chunk-based data, returning logical/physical lengths, device id, metadata flags, and hole state.
- Validates inline data does not cross a metadata block.
- `erofs_map_dev()` resolves device ids and flat-device offsets to block devices, files, fscache blobs, and DAX devices.
- Online folio helpers track split async completions, error state, and D-cache flushing in `folio->private`.
- Iomap operations map holes, inline data, and mapped extents for read, DAX, direct I/O, fiemap, bmap, SEEK_DATA, and SEEK_HOLE.
- `erofs_read_folio()` and `erofs_readahead()` use iomap reads, resolving shared inodes when page-cache sharing is enabled.
- File read supports DAX, direct I/O for block-backed uncompressed files, and buffered reads.
- File operations include llseek, read_iter, ioctl, mmap setup, splice, THP unmapped-area helper, and leases.

Important interactions:
- Compression fiemap delegates to `z_erofs_iomap_report_ops`.
- File-backed and fscache modes are selected through `internal.h` helpers.
- DAX mmap rejects shared writable mappings because EROFS is read-only.
