# File Research: sources/virtualization/nbdkit/plugins/python/examples/error.py

## Purpose
Example Python plugin that wraps a file but intentionally fails every odd I/O/extents call to test NBD client error handling.

## Main Entry Points
- `config()` accepts `file=`.
- `thread_model()` serializes all requests so seek-based I/O is safe.
- `open()` opens the configured file.
- `get_size()` returns file size.
- `can_extents()` enables extents.
- `extents()`, `pread()`, and `pwrite()` increment a global call counter and raise on odd calls.

## Dependencies
Uses `os`, `nbdkit`, API version 2 buffer protocol, `os.readv`/`writev`, and manual `lseek`.

## Risks and Notes
The global call counter is intentionally stateful and serialized by the thread model. File descriptors are not explicitly closed in a `close()` callback, which is acceptable for a small example but not ideal production style.
