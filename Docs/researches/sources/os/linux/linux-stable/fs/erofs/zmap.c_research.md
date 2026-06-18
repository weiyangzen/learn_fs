# File Research: sources/os/linux/linux-stable/fs/erofs/zmap.c

This file translates compressed EROFS logical offsets into physical compressed extents and implements FIEMAP reporting for compressed files.

Major responsibilities:
- Defines `struct z_erofs_maprecorder`, a transient decoder for compressed lcluster metadata.
- Loads full-format lcluster indexes with `z_erofs_load_full_lcluster()`.
- Loads compact-format lcluster indexes with `z_erofs_load_compact_lcluster()`, including 2-byte and 4-byte compact packs, lookback distances, big-pcluster compressed block counts, and derived physical block numbers.
- Loads extent-format compressed mappings with `z_erofs_map_blocks_ext()`, including binary search for variable records and compact sequential formats.
- Initializes compressed inode mapping metadata once in `z_erofs_fill_inode()`.
- Maps normal compressed layouts with `z_erofs_map_blocks_fo()`, handling nonhead lookback, tailpacking, fragments, partial refs, big pclusters, algorithm selection, and decompressed-length discovery.
- Exposes `z_erofs_map_blocks_iter()` as the main compressed block-mapping iterator.
- Implements `z_erofs_iomap_report_ops` for FIEMAP/reporting paths.

Important mapping behavior:
- Post-EOF mappings are reported as unmapped extents with a length that lets iomap progress.
- Fragment-only files can map the full file as `EROFS_MAP_FRAGMENT`.
- Ztailpacking maps inline compressed data as `EROFS_MAP_META` and validates that inline data does not cross a filesystem block.
- Fragment tail extents update inode fragment metadata during `EROFS_GET_BLOCKS_FINDTAIL`.
- Algorithm format is selected from plain/interlaced/shifted encodings or per-inode compressed algorithm slots.
- FIEMAP and readmore paths can force full decompressed-length calculation so extents are reported as complete rather than partial.

Validation:
- Rejects unknown lcluster types, invalid cluster offsets, bogus lookback distances, inconsistent big-pcluster features, unsupported algorithms, and invalid physical address ranges.
- Ensures advertised compression algorithms exist in the mounted superblock’s available-compressor bitmap.
- Rejects compressed extents whose physical length is impossible for the logical length, or plain extents whose physical length is too short.
- Enforces pcluster maximum compressed and decompressed sizes.
- Rejects physical ranges beyond the filesystem’s 48-bit physical block address limit.
