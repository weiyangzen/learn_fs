# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/wslist.cpp

## Role In Subset

Implements ARM3 working-set list management in C++ for process and system cache working sets. It tracks resident virtual pages through WSLEs, grows/shrinks WSLE backing storage, and trims cold pages under memory pressure.

## Main Responsibilities

- Maintains global `MmWorkingSetList` and `MmWorkingSetManagerEvent`.
- Allocates/free WSLE indexes with a compact free-list representation in `GetFreeWsleIndex` and `FreeWsleIndex`.
- Grows the WSLE array by allocating pages and making PTEs valid; shrinks excess backing pages when high indexes are freed.
- Inserts valid pages into a working set through `MiInsertInWorkingSetList`, recording virtual page, protection, direct/hashed flags, lock flags, and age.
- Removes pages with `MiRemoveFromWorkingSetList`.
- Initializes a working set list with fixed entries for paging structure mappings and the WSL itself.
- Implements `MmWorkingSetManager`, iterating `MmWorkingSetExpansionHead` and trimming eligible process working sets.

## Trimming Behavior

- `TrimWsList` scans dynamic entries, resets accessed bits on recently used pages, ages untouched pages, skips locked entries, skips page-table addresses, and converts sufficiently old valid PTEs into transition PTEs.
- When trimming, it marks dirty PFN state from the hardware dirty bit and decrements share count to place the page on standby/modified lists.
- Only direct WSLEs are supported.

## Locking And State Assumptions

- Insert/remove paths require exclusive working-set lock ownership.
- Trim scan requires a working-set lock and upgrades to exclusive before mutation.
- PFN changes use `ntoskrnl::MiPfnLockGuard`.
- Process working-set trimming attaches to the process after acquiring rundown protection, then detaches and releases protection.

## Notable Limitations

- Shared/prototype pages are not supported in this implementation path.
- ReactOS legacy PFNs are explicitly rejected.
- Session and system-space working sets are marked unsupported in the manager.
- Page-table address trimming is skipped because invalidating PDEs breaks legacy memory-manager assumptions.
- There is a temporary hack around PFN-embedded lock flags until fuller WSLIST support exists.

## Filesystem-Relevant Notes

Working-set trimming indirectly affects mapped-file and cache-backed pages by deciding when resident pages become transition pages. The current implementation is conservative and process-focused, with section/shared-page support still limited.
