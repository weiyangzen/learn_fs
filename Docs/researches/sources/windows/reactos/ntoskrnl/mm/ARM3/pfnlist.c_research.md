# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/pfnlist.c

This file implements PFN list manipulation for ARM3: free, zeroed, standby, modified, modified-no-write, bad, ROM-list metadata, colored page queues, available-page accounting, PFN initialization, and share/reference-count transitions.

Core globals:
- `MmZeroedPageListHead`, `MmFreePageListHead`, `MmStandbyPageListHead`, `MmModifiedPageListHead`, `MmModifiedNoWritePageListHead`, `MmBadPageListHead`, and `MmRomPageListHead` are the principal page-list heads.
- `MmStandbyPageListByPriority[8]` and `MmModifiedPageListByColor[1]` provide specialized queues.
- `MmPageLocationList[]` maps page-location enum values to list heads.
- `MmTransitionSharedPages` and `MmTotalPagesForPagingFile` track transition and paging-file-backed modified pages.
- PFN tracing state is stored in `MI_PFN_CURRENT_USAGE` and `MI_PFN_CURRENT_PROCESS_NAME`.

Main list operations:
- `MiIncrementAvailablePages` and `MiDecrementAvailablePages` maintain `MmAvailablePages` and signal/clear low/high memory events.
- `MiZeroPhysicalPage` maps a PFN through hyperspace and zeroes it.
- `MiUnlinkFreeOrZeroedPage` removes a PFN from the free or zeroed list and its colored list.
- `MiUnlinkPageFromList` removes transition pages from standby/modified lists and updates transition counters.
- `MiRemovePageByColor`, `MiRemoveAnyPage`, and `MiRemoveZeroPage` select and remove pages, preferring requested color lists where possible.
- `MiInsertPageInFreeList`, `MiInsertStandbyListAtFront`, and `MiInsertPageInList` insert pages into the appropriate list and auxiliary colored/priority structures.

PFN initialization:
- `MiInitializePfn` binds a physical page to a PTE, copies or synthesizes the original PTE, sets reference/share counts, marks it active and valid, sets modified state, determines the containing page-table PFN, and increments that page-table share count.
- `MiInitializePfnAndMakePteValid` is a combined PFN-init plus valid-PTE write helper.
- `MiInitializeAndChargePfn` allocates a zero page for a PDE, writes it valid, and initializes the PFN for another process/session.
- `MiInitializePfnForOtherProcess` initializes PFNs whose containing page table is supplied explicitly.

Reference and share count behavior:
- `MiDecrementShareCount` decrements mapping share count, converts prototype PTEs to transition PTEs when the last share disappears, and either frees deleted PFNs or drops references.
- `MiDecrementReferenceCount` handles ReactOS legacy PFNs via `MmDereferencePage`, validates counts, then puts fully unreferenced pages on the modified or standby list unless the PFN was deleted.
- Deleted PFNs are returned to the free list when their final reference disappears.

Important invariants:
- Most routines require the PFN lock and assert it.
- Free/zero lists are mirrored into per-color queues using `OriginalPte.u.Long` and `u4.PteFrame` as colored-list links.
- Free and zeroed pages must have zero reference and share counts.
- Transition pages are expected to be standby or modified pages, with prototype-PTE constraints in the supported ARM3 paths.
- `ASSERT_LIST_INVARIANT` verifies list heads are either fully empty or fully linked.

Notable limitations and risk points:
- Standby-list fallback in `MiRemoveAnyPage` and `MiRemoveZeroPage` is marked FIXME and not implemented.
- Modified-no-write list insertion/removal asserts false.
- Some modified-page support is limited to pagefile-backed single-prototype assumptions.
- There are several "ReactOS Hack" comments clearing `OriginalPte.u.Long` after unlinking, which shows the colored-list overlay is delicate.
- `MiDecrementReferenceCount` treats very high reference counts as corruption and asserts.
- Low-memory handling calls `MmRebalanceMemoryConsumers`, with comments noting missing modified-page-writer and working-set-manager wakeups.
