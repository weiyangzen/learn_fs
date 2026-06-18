# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/special.c

Read status: complete file, 694 lines.

This file implements ARM3 special pool support for ReactOS. Special pool routes selected pool allocations to a dedicated one-page allocation with a neighboring guard PTE, fills unused bytes with a pattern, and bugchecks on detected underruns, overruns, invalid frees, or invalid IRQL use.

Key entry points:
- `MmUseSpecialPool()` decides whether a request should use special pool based on allocation size and `MmSpecialPoolTag`, including wildcard tag support.
- `MmIsSpecialPoolAddress()` checks whether an address lies inside the reserved special-pool VA range.
- `MmIsSpecialPoolAddressFree()` checks whether the corresponding PTE is a free special-pool PTE rather than a guard marker.
- `MiInitializeSpecialPool()` reserves aligned system PTEs, builds a free list of PTE pairs, records extra reserve PTEs, sets nonpaged usage limits, and enables `POOL_FLAG_SPECIAL_POOL`.
- `MmExpandSpecialPool()` links another page worth of reserved PTE pairs into the free list when the active list is exhausted.
- `MmAllocateSpecialPool()` validates IRQL and limits, removes a PTE pair from the free list, allocates a physical page, maps it, chooses overrun or underrun layout, writes a `POOL_HEADER`, marks the guard PTE, fills the page with a tick-count byte pattern, and updates counters.
- `MiSpecialPoolCheckPattern()` verifies the post-buffer fill pattern.
- `MmFreeSpecialPool()` derives the header from the pointer layout, validates IRQL and guard markers, checks fill patterns, records freed-allocation metadata, unmaps or deletes the backing page, returns the PTE pair to the free list, and updates counters.
- `MiTestSpecialPool()` is a local stress/test helper for allocation/free and optional corruption tests.

Important state:
- `MmSpecialPoolStart` and `MmSpecialPoolEnd` define the reserved VA range.
- `MiSpecialPoolFirstPte`, `MiSpecialPoolLastPte`, `MiSpecialPoolExtra`, and `MiSpecialPoolExtraCount` manage the free PTE-pair list and reserves.
- `MmSpecialPagesInUse`, paged/nonpaged counters, and peak counters track special-pool consumption.
- `MiSpecialPagesNonPagedMaximum` caps nonpaged special-pool usage.
- `MmSpecialPoolCatchOverruns` chooses the default detection layout.
- PTE `PageFileHigh` values `SPECIAL_POOL_PAGED_PTE` and `SPECIAL_POOL_NONPAGED_PTE` mark guard PTEs.

Important dependencies:
- System PTE reservation through `MiReserveAlignedSystemPtes`.
- PFN allocation and mapping through `MiRemoveAnyPage`, `MiInitializePfnAndMakePteValid`, `MiDecrementShareCount`, and PFN lock helpers.
- Pool integration through `ExpPoolFlags`, `MmSpecialPoolTag`, and normal pool fallback when `MmAllocateSpecialPool()` returns `NULL`.
- Pageable-system-VM deletion through `MiDeleteSystemPageableVm()` for paged special-pool frees.

Notable behavior and risks:
- The special-pool VA range check uses `P <= MmSpecialPoolEnd`; `MmSpecialPoolEnd` is computed from the last PTE plus one, so this appears to include a one-past-end address.
- Special pool deliberately rejects allocations larger than one page minus `POOL_HEADER` and rejects the segment tag `'tSmM'` to avoid recursion with section prototype-PTE allocation.
- Alignment in `MiInitializeSpecialPool()` is disabled with a `FIXME`, so the reserved region may not honor the intended large alignment.
- Freed allocation records have placeholders for stack capture; `StackPointer` and `StackBytes` are not populated.
- Nonpaged free currently flushes the entire TLB with a `FIXME` to use single-address flushing.
- The verifier overlay header mentioned in `MI_FREED_SPECIAL_POOL` is still a TODO.
