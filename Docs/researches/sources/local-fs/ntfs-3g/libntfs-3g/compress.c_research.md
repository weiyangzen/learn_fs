# File Research: sources/local-fs/ntfs-3g/libntfs-3g/compress.c

## Role

Implements NTFS compressed attribute support, including LZNT-style compression/decompression, compressed attribute reads, compressed writes, runlist validation, sparse/hole handling, and final compression on close.

## Main Areas

### Compression Encoder

- `ntfs_hash()` hashes 3-byte sequences for match finding.
- `ntfs_best_match()` maintains a hash-chain dictionary and finds a bounded longest match with lazy parsing support.
- `ntfs_skip_position()` advances the match finder without emitting a match.
- `ntfs_compress_block()` compresses one 4096-byte NTFS sub-block, falling back to an uncompressed sub-block if compression is not beneficial.

Constants such as `NICE_MATCH_LEN`, `MAX_SEARCH_DEPTH`, `HASH_SHIFT`, and `NTFS_SB_SIZE` bound compression speed, memory, and sub-block layout.

### Decompression

- `ntfs_decompress()` decompresses a compression block into a destination buffer. It parses sub-block headers, tags, literal tokens, and phrase tokens.
- It zero-fills incomplete destination regions and returns `-1` with `errno = EOVERFLOW` for malformed streams or bounds violations.

### Compressed Reads

- `ntfs_is_cb_compressed()` determines whether a compression block is sparse, compressed, or fully uncompressed by inspecting the runlist.
- `ntfs_compressed_attr_pread()` reads from compressed attributes, handling resident fallback, encrypted rejection, initialized-size zero-fill, sparse compression blocks, uncompressed compression blocks, and actual decompression.

For raw compressed reads it temporarily clears compression state in `ntfs_attr` and adjusts sizes so `ntfs_attr_pread()` can read the physical compressed data.

### Compressed Writes

- `read_clusters()` and `write_clusters()` perform raw multi-run cluster I/O.
- `ntfs_comp_set()` compresses a set of sub-blocks, detects all-zero compressed blocks, writes rounded cluster-aligned compressed output, and returns special status values for sparse/all-zero/failure cases.
- `valid_compressed_run()` checks compressed runlist invariants: adjacency, hole alignment, and adjacent-hole validity.
- `ntfs_compress_overwr_free()` and `ntfs_compress_free()` free clusters no longer needed after compression and rewrite affected runlist segments.
- `ntfs_read_append()` loads/decompresses existing compressed data when appending into a partially compressed set.
- `ntfs_flush()` writes a full compression block either compressed or uncompressed.
- `ntfs_compressed_pwrite()` is the main compressed write path. It decides when a compression unit is full, reads previous data as needed, compresses, frees excess clusters, or writes uncompressed if compression is not possible.
- `ntfs_compressed_close()` compresses the last partial compression block at close time.

## Dependencies

Uses attribute I/O and metadata from `attrib.h`, volume layout from `volume.h`/`layout.h`, runlists from `runlist.h`, cluster allocation/freeing from `lcnalloc.h`, MST-independent raw device I/O indirectly through attributes, and logging/memory helpers.

## Important Behavior

The code assumes NTFS compression blocks are at least one 4096-byte sub-block. Encrypted compressed reads are rejected with `EACCES`. Several write paths require at least two unused runlist entries pre-reserved because cluster freeing may split runs and insert holes without reallocating the runlist.

Runlist integrity is critical: the compressed write path validates before and after mutation, and failures often return `EIO` because malformed compressed runlists imply metadata corruption.

## Research Notes

This is one of the highest-risk files in the group. It mutates allocation state, compressed size, and runlists while preserving NTFS compressed-run invariants. The most important integration points are `attrib.c` callers that route compressed reads/writes here and cluster allocator functions that free unused physical clusters after successful compression.
