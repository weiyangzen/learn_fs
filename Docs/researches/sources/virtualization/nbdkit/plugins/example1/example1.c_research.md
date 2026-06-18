# File Research: sources/virtualization/nbdkit/plugins/example1/example1.c

Minimal read-only in-memory nbdkit plugin example.

Key behavior:
- Defines a 100 MB static `data` array.
- Copies a predefined 512-byte boot sector into the disk at plugin load.
- Uses no per-connection handle.
- Exposes disk size as `sizeof(data)`.
- Implements `.pread` with a simple `memcpy`.
- Does not implement writes.

Educational focus:
- Demonstrates the smallest useful C plugin shape: `.load`, `.open`, `.get_size`, `.pread`, and registration.
- Chooses serialized thread model as a conservative example despite parallel reads being possible.
