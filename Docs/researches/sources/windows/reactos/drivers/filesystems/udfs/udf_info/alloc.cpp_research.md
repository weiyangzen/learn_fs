# File Research: sources/windows/reactos/drivers/filesystems/udfs/udf_info/alloc.cpp

## Purpose

`udf_info/alloc.cpp` implements UDF disk-space and bitmap management: partition address translation, bitmap run scanning, free-space allocation, used/free/bad/zero bitmap mutation, space accounting, write-cache allocation callbacks, and low-level bit operations.

## Address Translation

- `UDFPhysLbaToPart()` converts a physical LBA to a partition-relative logical block number for a requested partition.
- `UDFPartLbaToPhys()` converts `lb_addr` partition-relative addresses to physical LBAs, with compatibility recovery for invalid partition references when `UDF_VCB_IC_INSTANT_COMPAT_ALLOC_DESCS` is set.
- `UDFGetPartNumByPhysLba()` finds the partition containing a physical LBA.
- `UDFPartStart()`, `UDFPartEnd()`, and `UDFPartLen()` return partition boundaries/lengths, including special sentinel values for whole-media or last-partition behavior.

## Bitmap Scanning

- `UDFGetBitmapLen()` returns the length of a same-valued bit run starting at a bit offset and stopping before a limit.
  - It has an x86/MSVC assembly implementation and a generic C implementation.
- `UDFFindMinSuitableExtent()` scans the free-space bitmap for an extent:
  - prefers packet/write-block alignment when useful
  - honors sequential allocation flags
  - caps requests at `UDF_MAX_EXTENT_LENGTH`
  - returns the smallest extent satisfying the request, or the largest available extent if none is large enough
  - falls back from aligned to unaligned search when needed

## Allocation And Marking

- `UDFMarkBadSpaceAsUsed()` masks bad-space bitmap bits out of the free-space bitmap.
- `UDFMarkSpaceAsXXXNoProtect_()` marks all extents in a mapping as used, free, bad, or discarded without acquiring the bitmap resource.
  - updates `BitmapModified` and volume modified state
  - skips unallocated extents
  - clips extents at media boundary
  - updates FSBM, bad-space bitmap, zero-space bitmap, VAT entries, unmap/discard cache state, and mapping records depending on operation flags
- `UDFMarkSpaceAsXXX_()` wraps the no-protect function with exclusive `BitMapResource1` acquisition.
- `UDFAllocFreeExtent_()` allocates one or more extents for a requested byte length:
  - rounds length to logical block boundaries
  - scans within `[SearchStart, SearchLim)`
  - marks allocated blocks zero-filled
  - optionally verifies newly allocated extents with `UDFCheckArea()`
  - builds/merges extent mappings
  - rolls back partial allocation on disk-full or allocation failure

## Space Accounting

- `UDFGetPartFreeSpace()` counts free bits in a partition range using `bit_count_tab`.
- `UDFGetFreeSpace()` sums partition free space for normal media or computes appendable space from `NWA`/`LastLBA` for raw/CD-R style media.
- `UDFGetTotalSpace()` sums partition lengths or derives total media span depending on raw disk/CD-R mode.

## Cache Callback

`UDFIsBlockAllocated()` is a callback for write cache code. It reports `WCACHE_BLOCK_USED` and `WCACHE_BLOCK_ZERO` based on allocation and zero-filled bitmaps unless the VCB assumes all blocks are used.

## Low-Level Bit Operations

For x86 builds, the file supplies optimized bit helpers:

- `UDFGetBit__()`
- `UDFSetBit__()`
- `UDFSetBits__()`
- `UDFClrBit__()`
- `UDFClrBits__()`

Non-MSVC or non-assembly paths use simple C loops or direct shifts.

## Integration

This file is central to allocation code used by extent mapping, file resize/write paths, directory packing, VAT handling, bad-block handling, and write-cache correctness. It depends heavily on VCB partition maps and bitmap fields (`FSBM_Bitmap`, `BSBM_Bitmap`, `ZSBM_Bitmap`, `Vat`).

## Notable Risks

- Bitmap conventions are critical: free-space bits, used bits, bad bits, and zero bits are represented by different helper macros and must stay consistent.
- Several paths assume `BitMapResource1` is already held; misuse of the no-protect variant would corrupt allocation state.
- Assembly-specific implementations have C fallbacks, but behavior must remain bit-for-bit identical across compiler/platform configurations.
- The ReactOS comment in `UDFGetTotalSpace()` notes a fixed undefined shift value, indicating this code has had portability issues.
