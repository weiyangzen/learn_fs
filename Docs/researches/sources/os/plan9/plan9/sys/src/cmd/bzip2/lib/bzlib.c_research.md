# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzlib.c

Small libbzip2 support file.

Defines:

- `bz_config_ok()`: verifies expected type sizes: `int` 4 bytes, `short` 2 bytes, `char` 1 byte.
- `default_bzalloc()`: malloc-backed allocator.
- `default_bzfree()`: free-backed deallocator.
- `bz_internal_error()`: Plan 9-added fallback that exits with status 1.

This file supplies allocator/configuration glue used by compression and decompression initialization.
