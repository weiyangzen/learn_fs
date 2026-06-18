# File Research: sources/windows/reactos/ntoskrnl/mm/freelist.c

## Purpose

`freelist.c` implements legacy ReactOS physical-page accounting on top of the ARM3 PFN database. It provides free/in-use PFN predicates, single-page allocation and dereference helpers, MDL-backed physical-page allocation, reverse-map metadata storage, saved swap-entry storage, and a simple LRU list for user pages.

## Main Contents

- Defines global PFN/accounting variables including `MmPfnDatabase`, available page counters, commit counters, and `FirstUserLRUPfn`/`LastUserLRUPfn`.
- Maintains a user-page LRU chain through `MmGetLRUFirstUserPage`, `MmGetLRUNextUserPage`, `MmInsertLRULastUserPage`, and `MmRemoveLRUUserPage`.
- Classifies PFNs with `MiIsPfnFree`, `MiIsPfnInUse`, and public `MmIsPageInUse`.
- Allocates physical pages for MDLs with `MiAllocatePagesForMdl`, including range filtering, zeroed-page preference, MDL sizing fallback, PFN setup, and post-allocation zeroing.
- Stores per-PFN ReactOS metadata with `MmSetRmapListHeadPage`, `MmGetRmapListHeadPage`, `MmSetSavedSwapEntryPage`, and `MmGetSavedSwapEntryPage`.
- Manages legacy PFN references through `MmReferencePage`, `MmGetReferenceCountPage`, `MmDereferencePage`, and `MmAllocPage`.

## Behavior And Data Flow

`MmAllocPage` removes a zeroed page, marks it active, sets the reference count to one, marks it as a ReactOS PFN through `u4.AweAllocation`, clears swap/rmap fields, and optionally inserts user pages into the LRU list. `MmDereferencePage` decrements the PFN reference count and, when it reaches zero, removes cached user pages from the LRU list, clears the ReactOS-PFN marker, and returns the page to the ARM3 free list with `MiInsertPageInFreeList`.

`MiAllocatePagesForMdl` converts address bounds to PFNs, creates the largest MDL it can afford, removes pages either from any free page or from a caller-specified PFN range, initializes each PFN as a locked MDL allocation, zeroes pages not already on the zeroed list, and returns an MDL with `MDL_PAGES_LOCKED`.

## Concurrency And Invariants

- Most PFN mutations require the PFN lock and assert it with `MI_ASSERT_PFN_LOCK_HELD`.
- Reverse-map and swap-entry fields are stored in reused PFN fields and guarded by PFN locking where required.
- ReactOS-owned PFNs are asserted with `MI_IS_ROS_PFN`, encoded through `u4.AweAllocation`.
- User LRU operations assume nonzero PFNs and consistent `NextLRU`/`PreviousLRU` links.

## Notable Details

- The LRU list is explicitly described as a hack for paging-out behavior; `MmGetLRUNextUserPage` can move a still-shared page to the tail to avoid repeatedly selecting early mapped pages.
- `MiAllocatePagesForMdl` warns but does not fully support nonzero `SkipBytes`.
- MDL allocations may return fewer pages than requested, and the MDL byte count is adjusted to the found page count.
- `MiIsPfnFree` treats PFNs on low-numbered page lists with zero references and list links as available, so callers rely on PFN list state rather than only reference count.
