# File Research: sources/local-fs/dosfstools/src/io.c

Virtual disk I/O layer with optional deferred write queue.

Main behavior:
- `fs_open()` opens the target read-only or read-write and resets pending changes.
- `fs_read()` reads from the device/file and overlays any queued pending writes that overlap the requested range.
- `fs_test()` checks whether a byte range can be read fully.
- `fs_write()` either writes immediately when `write_immed` is set or appends a `CHANGE` record to an in-memory queue.
- `fs_flush()` writes queued changes in order and frees them.
- `fs_close(write)` flushes or discards queued changes, closes the descriptor, and returns whether changes existed.
- `fs_changed()` reports queued or immediate changes.

Research notes:
- Deferred writes let interactive fsck repair decisions be previewed before committing.
- Reads see queued changes, so later repair logic operates against the intended post-repair image even before flush.
- The file uses a single static file descriptor and queue, so the layer is process-global and single-target.
