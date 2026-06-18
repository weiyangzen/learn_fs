# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_region.h

Read completely: 108 lines.

This header defines `_citrus_region`, a pointer-plus-size view over a memory buffer, and inline helpers to initialize it, get the base pointer and length, bounds-check subranges, compute offsets, peek 8/16/32-bit values, and construct subregions.

Important interactions: mapped DB files, generated DB regions, mapper tables, pivot files, and memstreams all use this region abstraction. Multi-byte peeks copy with `memcpy`, avoiding unaligned-load issues; callers handle byte order explicitly where needed.

Security/reliability notes: `_citrus_region_check` uses `ofs + sz` directly, which can wrap on size_t overflow. Most callers use trusted or previously bounded offsets, but new file-format consumers should prefer an overflow-safe check pattern before deriving subregions from untrusted data.
