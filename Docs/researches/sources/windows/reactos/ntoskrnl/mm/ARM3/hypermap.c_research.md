# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/hypermap.c

## Purpose

`hypermap.c` implements ARM3 hyperspace and zeroing-space temporary mappings. These routines map physical pages into reserved kernel virtual PTE ranges for short-lived access and zeroing operations.

## Main State

- `MmFirstReservedMappingPte` and `MmLastReservedMappingPte` delimit the hyperspace mapping PTE range.
- `MiFirstReservedZeroingPte` points at the reserved zeroing PTE range.
- `HyperTemplatePte` is declared as a global template PTE, though this file uses `ValidKernelPte` and `ValidKernelPteLocal` directly.

## Hyperspace Mapping

`MiMapPageInHyperSpace`:

- requires a nonzero physical page with a valid PFN entry
- builds a local valid kernel PTE for the page
- asserts the target process is the current process
- acquires `Process->HyperSpaceLock`
- uses `MmFirstReservedMappingPte->PageFrameNumber` as a descending free-slot counter
- resets the counter to `MI_HYPERSPACE_PTES` and flushes the process TLB when exhausted
- writes the selected valid PTE and returns its virtual address

`MiUnmapPageInHyperSpace`:

- asserts the process is current
- clears the PTE for the mapped address
- releases `Process->HyperSpaceLock` at `DISPATCH_LEVEL`

The caller receives and must restore the old IRQL through the lock/unlock pair.

## Zeroing-Space Mapping

`MiMapPagesInZeroSpace`:

- requires `PASSIVE_LEVEL`
- maps up to `MI_ZERO_PTES` PFNs from a PFN linked list
- uses `MiFirstReservedZeroingPte->PageFrameNumber` as a descending allocation counter
- resets the zeroing PTE range and flushes the process TLB when there is not enough contiguous space
- writes noncached, write-through valid kernel PTEs for each PFN
- returns the virtual address of the first mapped PTE

`MiUnmapPagesInZeroSpace`:

- requires `PASSIVE_LEVEL`
- clears the mapped zeroing PTE range with `RtlZeroMemory`

## Notable Details

- The hyperspace path is serialized by the per-process `HyperSpaceLock`.
- The zeroing path has passive-level assertions but no explicit lock in this file.
- Both mechanisms use a PTE counter stored in the first reserved PTE rather than a separate global integer.
- Zeroing-space mappings explicitly disable cache and enable write-through, suitable for page zeroing semantics.
