# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_compr.c

This file implements decompression for NTFS compressed attribute data. `ntfs_uncompblock()` expands one 4 KiB NTFS compression block, handling both uncompressed block payloads and compressed tag/literal/back-reference streams. `ntfs_uncompunit()` walks a full NTFS compression unit and repeatedly calls `ntfs_uncompblock()` into the caller-provided uncompressed buffer.

The decompressor uses a local `GET_UINT16` macro for little in-memory 16-bit reads and relies on NTFS block/unit constants from `ntfs_compr.h`.

Dependencies: `ntfs.h`, `ntfs_compr.h`.

Research notes: this is read-path support only. It does not implement compression for writes. Bounds are mostly controlled by NTFS block-size constants and compressed block lengths.
