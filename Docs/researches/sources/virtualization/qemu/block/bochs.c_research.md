# File Research: sources/virtualization/qemu/block/bochs.c

This file implements read-only support for Bochs "growing" Redolog virtual disk images.

On-disk structures:
- `bochs_header` contains magic, type, subtype, version, header/catalog/bitmap/extent sizes, and disk-size fields for v1 and v2 layouts.
- Supported images must have magic `"Bochs Virtual HD Image"`, type `"Redolog"`, subtype `"Growing"`, and version `0x00010000` or `0x00020000`.

Open/probe:
- `bochs_probe()` returns strong confidence for matching headers.
- `bochs_open()` forces auto read-only because writes are unsupported, opens the file child, reads and validates the header, sets `total_sectors`, validates catalog size, allocates and loads the catalog bitmap, computes data offsets and extent/bitmap block counts, validates extent size, checks catalog coverage, and initializes a coroutine mutex.

Read mapping:
- `seek_to_sector()` maps a virtual sector to a file offset:
  - Calculates extent index and sector offset within the extent.
  - Treats catalog entry `0xffffffff` as unallocated.
  - Reads the extent bitmap byte and checks whether the sector is allocated.
  - Returns zero for unallocated sectors or the physical data offset for allocated sectors.
- `bochs_co_preadv()` enforces sector alignment, serializes reads with `s->lock`, iterates one sector at a time, reads allocated sectors from the file, and zero-fills unallocated sectors.

Limits and driver registration:
- `bochs_refresh_limits()` sets request alignment to 512 bytes.
- The driver is registered as a block format named `bochs`.

Filesystem/block relevance:
- This is a legacy image-format reader that exposes sparse Bochs growing disks as QEMU block devices.
- Its allocation bitmap handling is analogous to filesystem block mapping: unallocated virtual sectors read as zero.

Potential pitfalls:
- It is read-only.
- Reads are sector-by-sector, which is simple but potentially slow for large sequential reads.
- Catalog size is capped at one million entries to avoid unbounded allocation.
- Extent size must be a power of two between 512 bytes and 8 MiB.
