# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/sparse_io.c

Provides libext2fs I/O managers for Android sparse images: `sparse_io_manager` for filenames and `sparsefd_io_manager` for already-open fds. If `ENABLE_LIBSPARSE` is not enabled, both managers expose only open/close stubs returning `EXT2_ET_UNIMPLEMENTED`.

With libsparse enabled, it imports sparse chunks into an in-memory `blocks` array keyed by sparse block number, supports block-size remapping between ext2fs channel block size and sparse image block size, and writes the final sparse image on close. It implements read/write, partial negative-count I/O, discard/zeroout by freeing stored blocks, flush as a no-op, and readahead/set-option no-ops.

Important behavior: write-open truncates or uses the provided fd and rebuilds a sparse output file on close. Existing sparse images are imported through `sparse_file_foreach_chunk`. Writes past `blocks_count` silently stop. The parser accepts strings like `(file):blocks:block_size` or `(fd):blocks:block_size`.
