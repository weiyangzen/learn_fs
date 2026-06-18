# sources/storage-engines/wiredtiger/src/os_common/os_fstream.c

## Purpose
Provides a portable `WT_FSTREAM` implementation over WiredTiger file handles for line-oriented reads and buffered formatted writes.

## Important APIs, Types, and Functions
`__wt_fopen` creates stream handles. Private methods are `__fstream_close`, `__fstream_flush`, `__fstream_getline`, `__fstream_printf`, and not-supported variants for invalid read/write operations. `WT_STREAM_BUFSIZE` is 8192 bytes.

## Control Flow
Open wraps `__wt_open`, allocates a `WT_FSTREAM`, records file size, sets append offset if requested, and installs either write/append methods or read methods. `__fstream_getline` refills an internal buffer from `WT_FH` reads, discards empty lines, strips the newline, and NUL-terminates the caller buffer. `__fstream_printf` appends formatted output to the stream buffer, growing as needed, and flushes when the buffer reaches the stream size threshold. Close flushes non-read streams, closes the handle, frees buffers, and frees the stream.

## State and Persistence Behavior
Stream state includes the underlying `WT_FH`, current offset, total size, buffer, flags, and method table. Writes persist only when flushed or closed. Reads advance the stream offset and internal data pointer.

## Dependencies and Integration Points
Used by turtle/metadata backup text files and other code wanting portable file-stream behavior independent of libc stdio. It depends on common file handles, buffer allocation, formatted printing helpers, and `__wt_read`/`__wt_write`.

## Risks and Edge Cases
Empty lines are skipped and EOF is indicated by a returned buffer size of zero, which is a WiredTiger-specific contract. Switching method tables means calling `getline` on a write stream or `printf` on a read stream returns `ENOTSUP`. Buffered writes must be flushed before close errors are ignored by callers.

## Test Signals
Turtle file read/write, metadata backup loading, append-mode writes, long lines larger than 8192 bytes, empty-line skipping, and unsupported operation errors exercise this module.
