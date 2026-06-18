# File Research: sources/virtualization/spdk/lib/bdev/bdev_internal.h

`bdev_internal.h` is a small private header for bdev library internals. It declares the zero-buffer size constant, forward-declares core bdev types, and exposes internal helpers used by support files.

Declared helpers include obtaining a `spdk_bdev_io` from a channel, initializing and submitting bdev I/O, allocating/freeing I/O stats, and asynchronously resetting device stats. It also declares the reset-stat callback type.

Research notes: `bdev_zone.c` uses these helpers to allocate and submit zone-management I/O. `bdev_rpc.c` uses stat allocation and reset helpers for JSON-RPC I/O-stat endpoints.
