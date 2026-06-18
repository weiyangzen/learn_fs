# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/test_io.c

Implements `test_io_manager`, a wrapper I/O manager for libext2fs tests. It optionally delegates to `test_io_backing_manager` while logging or instrumenting operations.

Configuration is controlled by globals and environment variables. Callback globals can observe read/write/blocksize/write-byte operations. `TEST_IO_LOGFILE`, `TEST_IO_FLAGS`, `TEST_IO_BLOCK`, `TEST_IO_READ_ABORT`, and `TEST_IO_WRITE_ABORT` control output, logging flags, watched block, and intentional abort counts.

The manager supports open, close, set block size, read/write block, read/write block64, write byte, flush, set_option, get_stats, discard, cache_readahead, and zeroout. It can dump watched block contents with checksums and abort after configured read/write hits, making it useful for reproducible failure-injection tests.
