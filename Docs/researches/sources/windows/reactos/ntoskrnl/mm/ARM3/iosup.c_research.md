# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/iosup.c

## Purpose

`iosup.c` implements ARM3 I/O-space mapping helpers: `MmMapIoSpace`, `MmUnmapIoSpace`, video-display mapping wrappers, and an unimplemented active-I/O-space query.

## Cache Attribute Table

`MiPlatformCacheAttributes[2][MmMaximumCacheType]` maps public `MEMORY_CACHING_TYPE` values to internal `MI_PFN_CACHE_ATTRIBUTE` values for:

- RAM
- device memory / I/O mappings

For x86 in this file, both tables map cache types to `MiNonCached`, `MiCached`, and `MiWriteCombined` combinations.

## Mapping I/O Space

`MmMapIoSpace`:

- asserts a nonzero byte count
- asserts non-AMD64 physical addresses fit below 4 GB
- normalizes and validates `CacheType`
- computes page count from physical address plus size
- determines whether the PFN belongs to known RAM (`MiGetPfnEntry`) or I/O space
- translates the requested cache type through `MiPlatformCacheAttributes`
- reserves system PTEs from `SystemPteSpace`
- flushes TLB/cache before noncached or write-combined mappings
- adjusts the returned VA for the physical byte offset
- configures a valid kernel PTE template for cached, noncached/write-through, or write-combined mappings
- flushes again before installing PTEs
- writes one valid PTE per physical page

It returns the byte-offset-adjusted virtual address or `NULL` on invalid cache type/PTE allocation failure.

## Unmapping I/O Space

`MmUnmapIoSpace`:

- asserts a nonzero byte count
- computes the page count from base VA plus size
- gets the first PTE and PFN
- if the first PFN is not represented in the PFN database, clears the PTEs and flushes the TLB
- releases the system PTE range through `MiReleaseSystemPtes`

## Video Display Wrappers

- `MmMapVideoDisplay` is pageable and calls `MmMapIoSpace`.
- `MmUnmapVideoDisplay` calls `MmUnmapIoSpace`.

## Unimplemented API

`MmIsIoSpaceActive` is present but unimplemented and always returns `FALSE`.

## Notable Details

- Cache/TLB flushing is conservative around noncached and write-combined mappings.
- The unmap path only explicitly zeros PTEs when the mapping appears to be true I/O space outside the PFN database.
- PAE is called out as not respected by the current non-AMD64 high-part assertion.
