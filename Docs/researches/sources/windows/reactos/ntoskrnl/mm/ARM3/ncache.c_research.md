# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/ncache.c

## Role

`ncache.c` implements the noncached memory allocation and free APIs for ARM3: `MmAllocateNonCachedMemory` and `MmFreeNonCachedMemory`.

## Key mechanisms

- `MmAllocateNonCachedMemory` validates a nonzero byte count, computes the required page count, chooses the platform noncached cache attribute through `MiPlatformCacheAttributes[0][MmNonCached]`, and delegates physical page allocation to `MiAllocatePagesForMdl`.
- Rejects partial MDL allocations: it computes the pages spanned by the MDL virtual address and byte count and frees the MDL/pages if the returned page count is less than requested.
- Reserves system PTEs for the allocation plus one extra PTE. The extra PTE slot stores the MDL pointer so `MmFreeNonCachedMemory` can recover it from only the returned base address and size.
- Builds a valid kernel PTE template and adjusts cache bits for `MiNonCached` (`MI_PAGE_DISABLE_CACHE`, `MI_PAGE_WRITE_THROUGH`) or `MiWriteCombined` (`MI_PAGE_DISABLE_CACHE`, `MI_PAGE_WRITE_COMBINED`).
- Iterates the MDL PFN array and writes one valid PTE per page with `MI_WRITE_VALID_PTE`, returning the virtual address corresponding to the first real reserved PTE.
- `MmFreeNonCachedMemory` asserts nonzero size and page-aligned base, computes page count, finds the first mapping PTE, steps back to the hidden MDL pointer slot, frees pages and the MDL, then releases the full system PTE range including the extra slot.

## Dependencies and coupling

- Uses `miarm.h` for `MiAllocatePagesForMdl`, `MiReserveSystemPtes`, `MiReleaseSystemPtes`, `MiPteToAddress`, `MiAddressToPte`, `ValidKernelPte`, cache attribute tables, and PTE write/cache macros.
- Depends on MDL layout where PFN entries begin immediately after the `MDL` structure.
- Uses system PTE space as the virtual mapping substrate, so availability of system PTEs directly limits allocations.

## Limitations and risks

- The MDL pointer is hidden in the PTE immediately before the returned mapping. This is compact but makes correctness depend on freeing only exact addresses returned by `MmAllocateNonCachedMemory`.
- No runtime handling is present for a zero size or unaligned free address beyond assertions.
- Cache policy depends on `MiPlatformCacheAttributes`; the allocator itself only handles noncached/write-combined/silent default cases.
