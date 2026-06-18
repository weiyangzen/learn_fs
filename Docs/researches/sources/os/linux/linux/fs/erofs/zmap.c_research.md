# File Research: sources/os/linux/linux/fs/erofs/zmap.c

## Purpose
Translates EROFS compressed inode metadata into logical-to-physical block mappings for compressed reads and fiemap-style reporting.

## Main Elements
- Mapping recorder: `struct z_erofs_maprecorder` holds inode, target map, current logical cluster, cluster type, head type, deltas, physical block, compressed-block count, tail metadata offset, and metabox state.
- Full index loading: `z_erofs_load_full_lcluster()` reads standard lcluster indexes and decodes HEAD/NONHEAD type, cluster offset, deltas, partial references, physical block, and big-pcluster block counts.
- Compact index loading: `z_erofs_load_compact_lcluster()` decodes packed 2-byte/4-byte lcluster formats with bit extraction, special final-pack delta handling, big-pcluster CBLKCNT handling, and physical block reconstruction.
- Extent discovery: `z_erofs_extent_lookback()`, `z_erofs_get_extent_compressedlen()`, and `z_erofs_get_extent_decompressedlen()` find the head cluster, compressed byte length, and full decompressed span.
- Legacy/full-or-compact mapping: `z_erofs_map_blocks_fo()` handles normal compressed maps, ztailpacking inline data, fragment pclusters in the packed inode, partial references, algorithm selection, and readmore/fiemap expansion.
- Extent-style mapping: `z_erofs_map_blocks_ext()` supports newer extent records, including short records with implicit physical continuity, binary search over large logical starts, fragments, partial references, and shifted/interlaced/plain algorithm selection.
- Inode compression metadata initialization: `z_erofs_fill_inode()` reads the map header once per inode, initializes advise bits, cluster size, algorithms, extents, fragment offsets, inline tail data size, and validates big-pcluster feature consistency.
- Sanity checks: `z_erofs_map_sanity_check()` validates algorithm support, compressed and decompressed lengths, maximum pcluster sizes, and 48-bit physical address bounds.
- Public mapping and iomap reporting: `z_erofs_map_blocks_iter()` drives initialization and mapping; `z_erofs_iomap_report_ops` reports compressed extents, fragments, and holes through iomap.

## Dependencies And Integration
Used by `zdata.c` read and readahead paths, fiemap/reporting paths, EROFS metadata buffer APIs, inode compression fields, tracepoints, and superblock feature flags parsed in `super.c`.

## Risk Notes
The compact index decoder is bit-dense and relies on careful handling of special NONHEAD encodings, lookback/lookahead deltas, and old mkfs quirks. Mapping results are trusted by decompression I/O, so corruption checks for unsupported algorithms, impossible extents, pcluster limits, and 48-bit overflow are essential. Tailpacking and fragment handling mutate cached inode fields during initialization and must be serialized by the inode compression init bit lock.
