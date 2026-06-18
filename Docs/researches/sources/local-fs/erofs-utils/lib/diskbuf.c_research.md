# File Research: sources/local-fs/erofs-utils/lib/diskbuf.c

## Purpose
Temporary disk-backed buffer streams used to avoid creating too many temp files and to support large intermediate data.

## Main Structure
- `struct erofs_diskbufstrm`: stream fd, tail offset, device position, atomic reference count, alignment size, and simple lock flag.

## Important Functions
- `erofs_diskbuf_getfd()`: returns stream fd and absolute file position.
- `erofs_diskbuf_reserve()`: reserves current tail offset in a stream and increments refcount.
- `erofs_diskbuf_commit()`: advances stream tail by committed length.
- `erofs_diskbuf_close()`: releases a disk buffer reservation.
- `erofs_tmpfile()`: creates an unlinked temp file in `$TMPDIR` or `/tmp` with mode respecting umask.
- `erofs_diskbuf_init()`: initializes N streams, optionally using a duplicated image fd for stream 0 if it can be grown.
- `erofs_diskbuf_exit()`: validates refcounts, closes fds, and frees streams.

## Interactions
- Used by blob/fragments/importer-style staging paths.
- Uses global `g_sbi.bdev` for stream-0 optimization.

## Notes
The `locked` field has a TODO noting it is not a real multithreaded lock.
