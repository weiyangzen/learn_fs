# File Research: sources/local-fs/erofs-utils/lib/zmap.c

## Scope

This file maps compressed EROFS file logical offsets to physical compressed extents. It supports full indexes, compact indexes, newer extent records, big pclusters, fragments, tail packing, metabox-backed metadata, partial references, and FIEMAP-style full logical length discovery.

## Public And Internal APIs Covered

- Public iterator: `z_erofs_map_blocks_iter()`.
- Lazy inode initialization: `z_erofs_fill_inode_lazy()`.
- Full/compact index loaders: `z_erofs_load_full_lcluster()`, `z_erofs_load_compact_lcluster()`, and `z_erofs_load_lcluster_from_disk()`.
- Extent resolution helpers: `z_erofs_extent_lookback()`, `z_erofs_get_extent_compressedlen()`, `z_erofs_get_extent_decompressedlen()`, `z_erofs_map_blocks_fo()`, and `z_erofs_map_blocks_ext()`.
- Compact-bit helpers: `decode_compactedbits()` and `get_compacted_la_distance()`.

## Control Flow And Behavior

- Full indexes read one `z_erofs_lcluster_index` per logical cluster, recording type, cluster offset, pblk, partial-ref flag, nonhead deltas, and optional compressed-block count.
- Compact indexes compute the packed index region from the inode location, xattr size, cluster bits, initial 4-byte records, optional 2-byte records, and amortized pack size. They decode per-lcluster type/low bits, reconstruct nonhead deltas, derive pblk from the trailing base pblk plus preceding cluster count, and validate big-pcluster markers.
- `z_erofs_extent_lookback()` walks backward from a nonhead lcluster by delta until it finds the corresponding head lcluster and sets the map logical address to the head offset.
- `z_erofs_get_extent_compressedlen()` determines physical compressed length from head type and big-pcluster feature bits, defaulting to one block where allowed or reading the following CBLKCNT marker.
- `z_erofs_get_extent_decompressedlen()` advances through lclusters until EOF or next head to compute full decompressed extent length for FIEMAP-style queries.
- `z_erofs_map_blocks_fo()` handles full/compact-index mapping. It special-cases all-fragment files, maps logical offsets to head or nonhead extents, supports tail-packed inline compressed data, fragment pclusters, physical address calculation, compression algorithm selection, partial-ref flags, and optional full logical mapping.
- `z_erofs_map_blocks_ext()` handles extent-record layout. Depending on record size, it uses implicit sequential physical addresses, fixed lcluster records, or binary search over explicit logical starts. It detects final fragment extents and decodes plen flags into mapped/full/encoded/partial-ref flags and algorithm format.
- `z_erofs_fill_inode_lazy()` reads the compressed map header once per inode, handles the special packed-inode whole-file fragment marker, initializes z-advise flags, lcluster bits, algorithm ids, extent count, fragment offset, inline pcluster size, and tail extent metadata.
- `z_erofs_map_blocks_iter()` returns an unmapped post-EOF extent when `m_la >= i_size`; otherwise it initializes compressed metadata, dispatches to extent or full/compact mapping, and rejects encoded pclusters above maximum physical or decompressed sizes.

## State And Data Structures

- `struct z_erofs_maprecorder` carries current inode, output map, lcn, type/head type, cluster offset, deltas, pblk, compressed block count, next packed offset, and partial-ref flag.
- Populates `struct erofs_map_blocks` fields including `m_la`, `m_pa`, `m_llen`, `m_plen`, `m_flags`, `m_algorithmformat`, and metadata buffer cursor.
- Updates compressed inode fields such as `z_advise`, `z_lclusterbits`, `z_algorithmtype`, `z_idata_size`, `z_fragmentoff`, `fragmentoff`, `z_extents`, and `z_tailextent_headlcn`.

## Dependencies

- Depends on EROFS internal compressed-format macros, metadata buffer reads, inode location helpers, metabox detection, endian conversion, and map flag definitions.

## Risks And Invariants

- Compact index decoding is highly format-sensitive: pack alignment, lcluster bit limits, D0/D1 deltas, and big-pcluster flags must match mkfs output exactly.
- Corruption checks reject unknown lcluster types, invalid cluster offsets, impossible lookback distances, missing CBLKCNT markers, inconsistent algorithm availability, and oversized pclusters.
- Tail-packing and fragment handling mutate inode tail fields during `FINDTAIL`; callers rely on lazy initialization being idempotent.
- Extent binary search assumes sorted extent logical starts and validates that discovered right boundary does not exceed current logical end.
