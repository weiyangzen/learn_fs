# File Research: sources/local-fs/squashfs-tools/squashfs-tools/reader.c

Concurrent source-file reader for mksquashfs. It classifies files into block-reader and fragment-reader arrays, creates per-reader caches, reads file data into `file_buffer`s, and routes buffers to deflate, fragment processing, or main assembly queues.

It supports regular files, dynamic pseudo process files, and pseudo data records. Regular file reading detects sparse files using `SEEK_DATA`, emits sparse buffers, and restats/retries when file size changes during reading, with a version cap. Dynamic pseudo process output is read until EOF, then child status is checked before final buffer routing.

Pseudo data reading supports seekable pseudo data files and stdin. For stdin, it implements a readahead table so out-of-order reads can retrieve already consumed ranges or buffer ahead to later offsets.

Threading modes include single reader, split small/block readers, and tar handling. `readers_sane()` enforces compile-time single-reader default rules when applicable. `initial_reader()` chooses tar, multi-threaded, or single-threaded paths and can install an interval timer for I/O throttling.

Memory sizing is validated in `check_min_memory()`, which computes per-reader and writer queue block budgets and emits actionable alternatives before fatal error.
