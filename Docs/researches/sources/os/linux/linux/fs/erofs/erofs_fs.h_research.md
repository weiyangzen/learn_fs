# File Research: sources/os/linux/linux/fs/erofs/erofs_fs.h

Defines the EROFS on-disk format.

Key behavior:
- Defines superblock offset, compatible/incompatible feature bits, and full incompatible-feature mask.
- Defines device slot format and 144-byte superblock layout, including 48-bit block/root fields, compression algorithm bitmap, device table metadata, packed/metabox inode nids, xattr prefix metadata, and build time.
- Defines inode data layouts: flat plain, compressed full, flat inline, compressed compact, and chunk-based.
- Defines compact and extended inode layouts.
- Defines inline/shared xattr headers, xattr entry format, long xattr prefixes, name filters, and xattr sizing helpers.
- Defines chunk mapping formats, null address marker, block-map entry, chunk index, directory entry format, and max name length.
- Defines compression algorithm ids and config records for LZ4, LZMA, DEFLATE, and ZSTD.
- Defines compressed map headers, lcluster indexes, extent records, advise bits, and extent record sizing.
- `erofs_check_ondisk_layout_definitions()` uses build-time assertions to lock structure sizes and layout assumptions.

Important interactions:
- Shared with userspace tooling and kernel implementation; changes here are on-disk format changes.
- Many runtime checks in `inode.c`, `data.c`, and decompressor code interpret these fields.
