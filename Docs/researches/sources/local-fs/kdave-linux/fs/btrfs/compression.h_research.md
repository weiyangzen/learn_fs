# File Research: sources/local-fs/kdave-linux/fs/btrfs/compression.h

Public Btrfs compression interface shared by compressed I/O, algorithm implementations, and defrag/compression callers.

Key responsibilities:
- Defines compressed extent limits: 128 KiB maximum on-disk compressed size, 128 KiB maximum uncompressed size, and 512 KiB worker chunk size.
- Defines `struct compressed_bio`, which wraps a `btrfs_bio` with file offset, logical length, compression type, writeback mode, and original read bio pointer.
- Provides helpers for deriving filesystem info from a compressed bio and computing per-folio input lengths.
- Declares global compression lifecycle, per-filesystem workspace manager allocation/free, compressed read/write submission, and compressed bio allocation.
- Defines `struct workspace_manager` for idle workspace lists, spinlock protection, counters, and waiters.
- Declares compression level metadata and algorithm-specific zlib, lzo, and zstd workspace/compress/decompress hooks.
- Provides `cleanup_compressed_bio()` for releasing all compressed folios attached to a compressed bio.

Dependencies:
- Includes Linux mm, list, workqueue, wait, and page-cache interfaces.
- Includes Btrfs bio, fs, and inode headers.
- Relies on UAPI compression type constants and Btrfs folio free helpers.

Notable risks:
- `compressed_bio` requires `bbio` to stay last because allocation embeds it through bioset offset arithmetic.
- Maximum compressed page count is derived from `PAGE_SIZE`; folio/block-size variants require matching assumptions in implementation code.
- Cleanup assumes every folio in the bio was allocated with `btrfs_alloc_compr_folio()`.
