# File Research: sources/virtualization/spdk/lib/ftl/ftl_internal.h

## Purpose
Defines shared internal constants, address types, P2L map structures, trim log format, and cross-module internal prototypes for FTL.

## Key Constants And Types
- `FTL_ADDR_INVALID`, `FTL_LBA_INVALID`, and `FTL_BLOCK_SIZE` of 4096 bytes.
- P2L and P2L-log metadata version constants.
- `typedef uint64_t ftl_addr`, where addresses below base size point to base bdev and higher addresses point into NV cache.
- `enum ftl_md_type`, `enum ftl_band_type`, and `enum ftl_md_status`.

## Metadata Structures
- `struct ftl_p2l_map_entry`: LBA plus sequence ID.
- `struct ftl_p2l_map`: valid count, refcount, valid bitmap, runtime map pointer, DMA metadata entry pointer, and checkpoint reference.
- `struct ftl_p2l_ckpt_page` and `_no_vss` describe persisted P2L checkpoint page formats.
- `struct ftl_trim_log` is exactly one FTL block and stores trim VSS header plus padding.

## API Groups
Declares P2L checkpoint lifecycle/restore/persist APIs, relocation lifecycle, P2L log lifecycle/flush/acquire/release/read APIs, and management helpers.

## Dependencies
Includes SPDK stdinc/CRC/util/uuid/ftl plus FTL bitmap and metadata utility headers.
