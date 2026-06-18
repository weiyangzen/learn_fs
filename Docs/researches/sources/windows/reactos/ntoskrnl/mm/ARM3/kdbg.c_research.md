# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/kdbg.c

## Purpose

`kdbg.c` provides debug-only ARM3 kernel debugger extensions for inspecting pool allocations, pool tag usage, finding pool allocations by tag, and finding IRPs. The implementation is compiled only under `DBG && KDBG`.

## Shared Definitions

The file duplicates pool block helper macros from `expool.c` and imports:

- `MmNonPagedPoolEnd0`
- `PoolBigPageTableSize`
- `PoolBigPageTable`
- `MiDumpPoolConsumers`

It defines `IRP_FIND_CTXT` for IRP search filters and uses `POOL_BIG_TABLE_ENTRY_FREE` to identify unused large-pool tracker entries.

## Pool Page Dump

`ExpKdbgExtPool`:

- accepts an address and optional flags
- page-aligns the address to identify a pool page
- validates accessibility with `MmIsAddressValid`
- reports whether the address lies in paged or nonpaged pool
- walks pool entries in that page
- marks the entry containing the target address
- optionally dumps the first eight ULONGs of block payload data

Without an address, heap-wide dumping is reported as unimplemented.

## Pool Used Dump

`ExpKdbgExtPoolUsed` parses optional flags and tag filters, then calls `MiDumpPoolConsumers(TRUE, Tag, Mask, Flags)`.

`ExpKdbgExtPoolUsedGetTag` parses up to four tag characters and builds a byte mask so `?` can act as a wildcard.

## Pool Search

`ExpKdbgExtPoolFind` searches for allocations by tag and optional pool type:

- first scans the large-pool allocation table with `ExpKdbgExtPoolFindLargePool`
- then scans either nonpaged pool or paged pool

Large-pool scanning:

- skips free entries
- matches `(Key & Mask) == (Tag & Mask)`
- either invokes a callback or prints address, tag, and size

Paged-pool scanning:

- uses `MmPagedPoolInfo.PagedPoolAllocationMap` to find allocated pool pages
- validates address range and expansion boundary
- scans possible header offsets within each page
- uses `ExpKdbgExtValidatePoolHeader`
- prints matching entries or invokes a callback

Nonpaged-pool scanning:

- brute-force scans from `MmNonPagedPoolStart` to `MmNonPagedPoolEnd0`
- stops at `MmNonPagedPoolExpansionStart`
- validates mapped pages and candidate headers
- prints matching entries or invokes a callback

## Header Validation

`ExpKdbgExtValidatePoolHeader` rejects candidate headers when:

- `BlockSize` is zero/negative
- the block would extend past the containing page
- `PreviousSize` is inconsistent with page position
- pool type does not match the region being scanned
- the tag has suspicious high-bit bytes according to `(PoolTag & 0x00808080)`

The scanner advances in 8-byte increments because it is searching for plausible headers, not walking only trusted block chains.

## IRP Finder

`ExpKdbgExtIrpFind` scans pool allocations with `TAG_IRP` in paged or nonpaged pool and uses `ExpKdbgExtIrpFindPrint` as a callback.

Supported filters:

- restart address
- device object
- original file object
- MDL process
- thread
- user event
- all argument-style criteria with `arg`

`ExpKdbgExtIrpFindPrint` skips free entries, reconstructs the IRP from the pool payload, validates current stack location bounds, extracts the driver name when possible, applies filter criteria, and prints either current stack information or a completed-IRP status.

## Notable Details

- This file is diagnostic tooling only; it has no retail runtime path outside `DBG && KDBG`.
- Paged-pool scanning uses the allocation bitmap for speed, while nonpaged scanning is brute force.
- Large allocations are found through the big pool table, so they do not depend on small-pool page headers.
- Pool type argument handling only accepts `0` and `1` for nonpaged/paged pool.
