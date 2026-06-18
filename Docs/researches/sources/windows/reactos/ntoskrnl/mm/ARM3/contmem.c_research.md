# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/contmem.c

Read status: complete file, 676 lines.

This file implements ARM3 contiguous physical memory allocation and freeing, backing the public `MmAllocateContiguousMemory*` and `MmFreeContiguousMemory*` APIs.

Key entry points:
- `MiFindContiguousPages()` scans `MmPhysicalMemoryBlock` runs for free PFNs within caller bounds and optional boundary constraints, then revalidates under the PFN lock, unlinks pages from free/zeroed lists, marks PFN state, and tags allocation start/end PFNs.
- `MiCheckForContiguousMemory()` verifies whether an existing virtual range maps a physically contiguous PFN sequence satisfying low/high/boundary constraints.
- `MiFindContiguousMemory()` calls `MiFindContiguousPages()`, maps the selected physical range through `MmMapIoSpace()`, and fixes PFN `PteAddress`/`PteFrame` metadata to match the mapping.
- `MiAllocateContiguousMemory()` first tries cached nonpaged-pool allocation and validates physical contiguity, then falls back to PFN-run search if IRQL permits.
- `MiFreeContiguousMemory()` frees pool-backed contiguous allocations directly, otherwise validates the start PFN marker, marks PFNs deleted, unmaps the I/O-space mapping, and decrements share counts under the PFN lock.
- Public wrappers `MmAllocateContiguousMemorySpecifyCache()`, `MmAllocateContiguousMemory()`, `MmFreeContiguousMemory()`, and `MmFreeContiguousMemorySpecifyCache()` convert address bounds and delegate to internal helpers.

Important dependencies:
- PFN database helpers/macros: `MI_PFN_ELEMENT`, `MiGetPfnEntry`, `MiIsPfnInUse`, `MiUnlinkFreeOrZeroedPage`, `MiAcquirePfnLock`, `MiReleasePfnLock`, `MiDecrementShareCount`.
- Address/PTE helpers: `MiAddressToPte`, `MiPteToAddress`, `PFN_FROM_PTE`.
- Pool and I/O mapping APIs: `ExAllocatePoolWithTag`, `ExFreePoolWithTag`, `MmMapIoSpace`, `MmUnmapIoSpace`.
- Global layout bounds: `MmNonPagedPoolStart`, `MmNonPagedPoolExpansionStart`, `MmNonPagedPoolEnd`, `MmHighestPhysicalPage`.

Notable behavior and risks:
- Boundary handling converts `BoundaryPfn` to `~(BoundaryPfn - 1)`; zero boundary is accepted only because guarded checks skip use when `BoundaryPfn` is zero.
- Cached allocations prefer nonpaged pool because initial nonpaged pool is expected to be contiguous, but expansion allocations may fail the explicit PFN-contiguity check.
- The allocator refuses the PFN-search fallback above APC_LEVEL.
- Freeing a non-pool allocation from the middle of an allocation triggers `BAD_POOL_CALLER` with code `0x60`.
- Public `MmFreeContiguousMemorySpecifyCache()` ignores size and cache type during free, intentionally delegating to the generic free path.
