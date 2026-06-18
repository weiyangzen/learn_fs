# File Research: sources/virtualization/nbdkit/plugins/example3/example3.c

Simple read-write plugin using a per-connection temporary sparse file.

Key behavior:
- Optional `size=<SIZE>` parameter, defaulting to 100 MB.
- Creates an unlinked temporary file per connection under `LARGE_TMPDIR`.
- Uses `ftruncate` to create a sparse file of the requested size.
- Implements `.pread`, `.pwrite`, and `.flush`.
- Flush uses `fdatasync`, falling back to `fsync` if unavailable.
- Ignores readonly mode intentionally for this example.

Educational focus:
- Demonstrates read-write plugin callbacks, temporary backing storage, config parsing with `nbdkit_parse_size`, and per-connection isolation.
