# File Research: sources/local-fs/kdave-linux/fs/btrfs/compression.c

Btrfs compressed I/O implementation for zlib, lzo, and zstd, including compressed read/write bio handling, compression workspace management, cached compression folios, and compressibility heuristics.

Key responsibilities:
- Maps compression types to strings, validates type names, parses compression levels, and clamps levels to algorithm-supported ranges.
- Allocates `compressed_bio` instances from a dedicated bioset and routes reads/writes through algorithm-specific compression/decompression backends.
- Maintains a global cached folio pool for compression pages, with shrinker integration and fallback allocation for larger block-size cases.
- Submits compressed writes, completes ordered extents, clears writeback on original file-cache folios, and frees compressed folios after I/O.
- Submits compressed reads by allocating folios for on-disk compressed data, optionally adding readahead pages from the same compressed extent, then decompressing into the original bio.
- Manages per-filesystem compression workspace managers for heuristic, zlib, lzo, and zstd paths, with preallocation and wait queues for forward progress.
- Provides inline/small decompression helpers and `btrfs_decompress_buf2page()` to copy decompressed buffers into requested bio ranges.
- Implements the compression heuristic using systematic sampling, byte-set size, core-byte distribution, repeated-pattern detection, and Shannon entropy estimation.

Dependencies:
- Uses Btrfs bio, ordered extent, extent map, extent I/O, subpage, inode, filesystem, and message infrastructure.
- Calls algorithm-specific helpers declared in `compression.h` and implemented in zlib/lzo/zstd modules.
- Depends on kernel folio/page cache APIs, biosets, shrinkers, PSI memstall accounting, wait queues, and GFP allocation controls.

Notable risks:
- Workspace allocation intentionally waits instead of returning errors; failed initial preallocation can still lead to low-memory retry loops.
- Compressed read readahead has special cases for subpage and block-size-greater-than-page-size filesystems, so behavior differs across sector/page configurations.
- `btrfs_compress_is_valid_type()` treats a matching prefix as valid, so callers must separately handle suffix parsing and option boundaries.
- Heuristic sampling assumes source pages are present and maps pages directly; callers must only use it in contexts where the page-cache range is valid.
- Bio length, folio order, sector alignment, and original bio advancement are tightly coupled and corruption-prone if caller invariants change.
