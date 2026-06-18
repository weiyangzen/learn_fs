# File Research: sources/os/linux/linux/mm/hmm.c

## Purpose

`hmm.c` implements core Heterogeneous Memory Management range-fault and DMA-map helpers. It lets device drivers inspect a process address range as PFN entries, optionally fault CPU page tables to satisfy requested access, represent device-private and migration entries, and map valid PFNs for DMA including PCI P2PDMA handling.

## Major Responsibilities

- Walk process page tables for an `hmm_range`.
- Fill `range->hmm_pfns[]` with PFNs plus HMM flags such as valid, writable, order, error, DMA mapped, and P2PDMA state.
- Decide when a missing or insufficient mapping must be faulted in based on default range flags and per-PFN request flags.
- Handle PTE holes, non-present PTEs, migration entries, device-private entries, transparent huge PMDs, huge PUDs, and hugetlb mappings.
- Reject unsupported VMAs or mark them as `HMM_PFN_ERROR`.
- Coordinate with mmu interval notifiers so callers retry if invalidation raced with the walk.
- Allocate, free, map, and unmap HMM DMA mapping state.

## Range Fault State and Flags

`struct hmm_vma_walk` stores the active `hmm_range` and `last`, the next address that still needs processing after a retryable fault or migration wait.

Internal fault flags are:

- `HMM_NEED_FAULT`
- `HMM_NEED_WRITE_FAULT`
- `HMM_NEED_ALL_BITS`

`HMM_PFN_INOUT_FLAGS` preserves selected caller-owned output/input bits across PFN replacement: `HMM_PFN_DMA_MAPPED`, `HMM_PFN_P2PDMA`, and `HMM_PFN_P2PDMA_BUS`.

`hmm_pte_need_fault()` combines per-PFN request flags masked by `range->pfn_flags_mask` with `range->default_flags`. It requests a normal fault if the CPU mapping is not valid, and a write fault if write access was requested but the CPU mapping is not writable.

`hmm_range_need_fault()` applies that decision over a contiguous set of PFN entries and stops once both read and write fault requirements are known.

## Page Table Walking

The walker is registered through `hmm_walk_ops`:

- `.pud_entry = hmm_vma_walk_pud`
- `.pmd_entry = hmm_vma_walk_pmd`
- `.pte_hole = hmm_vma_walk_hole`
- `.hugetlb_entry = hmm_vma_walk_hugetlb_entry`
- `.test_walk = hmm_vma_walk_test`
- `.walk_lock = PGWALK_RDLOCK`

`hmm_range_fault()` requires the caller to hold `mmap_lock`, checks `mmu_interval_check_retry()` before each walk, and repeats on `-EBUSY`. A retry means some part of the range was faulted or waited on; entries before `last` are already output entries and entries at or after `last` still contain input request flags.

## Holes, PTEs, and Non-Present Entries

`hmm_vma_walk_hole()` handles missing page-table levels or PTE holes. If the range requested faults and a VMA exists, it calls `hmm_vma_fault()`. Without a VMA, requested faults fail with `-EFAULT`; otherwise the PFN array is filled with `HMM_PFN_ERROR`. Non-faulting holes inside a VMA are filled with zero flags.

`hmm_vma_handle_pte()` handles individual PTEs:

- Empty PTEs and UFFD-WP markers fault if requested, otherwise report no CPU mapping.
- Device-private entries owned by `range->dev_private_owner` are reported directly as valid PFNs without faulting.
- Swap, device-private, and device-exclusive entries fault if the caller requested a valid mapping.
- Migration entries wait with `migration_entry_wait()` and return `-EBUSY`.
- Unsupported non-present entries fail with `-EFAULT`.
- Present normal pages produce `pte_pfn(pte) | HMM_PFN_VALID` and optionally `HMM_PFN_WRITE`.
- Present mappings without a normal page, except zero PFNs, become `HMM_PFN_ERROR` unless the caller requested a fault.

When `hmm_vma_handle_pte()` faults or waits, it unmaps the PTE before returning.

## Huge and Migration Handling

For transparent huge PMDs, `hmm_vma_handle_pmd()` computes a PMD-sized order flag, verifies requested access, and fills every base-page PFN entry with the huge mapping's PFN plus valid/write/order flags. It does not split THPs merely to inspect them.

`hmm_vma_walk_pmd()` handles PMD holes, PMD migration entries, absent PMDs, transparent huge PMDs, bad PMDs, and normal PTE tables. If THP migration is supported, `hmm_vma_handle_absent_pmd()` can report device-private PMD entries owned by the caller; otherwise absent unsupported PMDs are errors unless no valid mapping was requested.

When architecture huge PUD support is enabled, `hmm_vma_walk_pud()` locks a huge PUD, reports PUD-sized mappings similarly to PMDs, or asks the generic walker to descend into the subtree.

For hugetlb VMAs, `hmm_vma_walk_hugetlb_entry()` locks the huge PTE, checks requested access, and fills PFNs with the huge-page order. If a fault is needed, it drops both the huge PTE lock and hugetlb VMA read lock before calling `hmm_vma_fault()` to avoid deadlock, then reacquires the VMA lock before returning.

## VMA Filtering

`hmm_vma_walk_test()` permits readable VMAs that are not `VM_IO` and not `VM_PFNMAP`. Unsupported VMAs cannot be represented safely by HMM. If the caller requested faults, unsupported ranges fail with `-EFAULT`; otherwise their PFNs are filled with `HMM_PFN_ERROR` and the walker skips to the next VMA.

## DMA Map Helpers

`hmm_dma_map_alloc()` allocates `map->pfn_list`, optionally allocates a DMA address list, and tries to allocate an IOVA state. It rejects devices that require DMA sync or have limited DMA addressing because HMM cannot follow the usual DMA buffer ownership transfer model and cannot tolerate SWIOTLB-style bounce buffering.

`hmm_dma_map_free()` frees IOVA state, PFN storage, and DMA-address storage.

`hmm_dma_map_pfn()` maps one HMM PFN entry:

- Reuses existing DMA mappings when possible.
- Handles PCI P2PDMA states: no P2P, P2P through host bridge with `DMA_ATTR_MMIO`, or direct bus-address mapping.
- Uses `dma_iova_link()` and `dma_iova_sync()` when IOVA state is active.
- Otherwise uses `dma_map_phys()` and stores the DMA address if the device needs explicit unmap.
- Marks the PFN entry with `HMM_PFN_DMA_MAPPED` and any P2PDMA flags.

`hmm_dma_unmap_pfn()` reverses the mapping if the PFN is both valid and DMA mapped. Bus-address P2PDMA mappings do not require unmap; IOVA and explicit DMA mappings are unlinked or unmapped as appropriate. It clears DMA/P2PDMA bits from the PFN entry.

## Integration Points

HMM bridges process page tables, device-private memory, migration, mmu interval notifiers, DMA mapping, PCI P2PDMA, hugetlb, transparent huge pages, and driver-owned PFN arrays. Its main contract is retry-oriented: drivers must tolerate `-EBUSY`, revalidate against mmu notifier sequences, and treat PFN-array entries as a snapshot that can be invalidated by concurrent CPU memory-management activity.
