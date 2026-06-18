# File Research: sources/windows/reactos/ntoskrnl/mm/i386/pagepae.c

## Purpose

`pagepae.c` is an older i386 low-level paging implementation that supports both non-PAE and PAE at runtime through `Ke386Pae`. It manages process page directories, hyperspace mappings, page-table allocation/freeing, PTE reads/writes, swap PTEs, dirty bits, protection changes, TLB flushing, and global kernel page-directory snapshots.

## Main Contents

- Defines non-PAE and PAE hardware bit masks, address-to-PDE/PTE macros, hyperspace layout macros, and global kernel page-directory arrays.
- Implements SMP-aware TLB flushing through `MiFlushTlbIpiRoutine` and `MiFlushTlb`.
- Converts page protections with `ProtectToPTE`.
- Creates process address spaces in `MmCreateProcessAddressSpace`, allocating page-directory/table pages and wiring PTE base plus hyperspace self-mappings.
- Frees empty page tables through `MmFreePageTable`.
- Locates or creates PTE slots through `MmGetPageTableForProcessForPAE` and `MmGetPageTableForProcess`, including hyperspace access for non-current processes.
- Reads PTEs through `MmGetPageEntryForProcessForPAE` and `MmGetPageEntryForProcess`.
- Implements mapping deletion, pagefile mapping creation/deletion, mapping creation, dirty-bit updates, protection queries/updates, present/swap checks, and PFN lookup.
- Initializes global kernel PDE snapshots through `MmInitGlobalKernelPageDirectory`.

## Behavior And Data Flow

The file has parallel PAE and non-PAE branches for almost every operation. PAE paths operate on 64-bit PTEs and use `Exf*64`/`Exfp*64` interlocked operations; non-PAE paths operate on 32-bit PTEs. Page-table lookup creates missing page tables when requested and, for kernel addresses, first populates a global kernel directory entry and then synchronizes the current process directory from it.

`MmCreateVirtualMappingUnsafe` maps an array of PFNs over a virtual range, creating page tables as needed, marking PFNs mapped, replacing any prior mapped PFN, updating optional per-process page-table reference counts, and flushing stale translations. `MmDeleteVirtualMapping` atomically clears the PTE, marks the PFN unmapped if a page was present, returns dirty/PFN data, decrements page-table reference counts, and frees an empty page table.

## Concurrency And Invariants

- PTE replacement is interlocked; 64-bit PAE operations use explicit compare/exchange or exchange helpers.
- Hyperspace mappings are unmapped with `MmUnmapPageTable`, which distinguishes direct recursive PTE-space addresses from temporary hyperspace mappings.
- Per-address-space `PageTableRefCountTable` entries are incremented/decremented for user mappings and can trigger `MmFreePageTable`.
- Kernel PDEs are cached in global arrays and synchronized into process page directories.
- Nonzero physical bits in an invalid PTE are treated carefully: present pages and swap entries share invalid-PTE encodings.

## Notable Details

- The file has a different public signature for `MmCreateVirtualMappingUnsafe` and `MmCreateVirtualMapping` than `page.c`: it accepts an array of PFNs and a page count.
- NX support is partially encoded with high bits when `Ke386NoExecute` is set.
- Some failures assert instead of returning recoverable errors, reflecting low-level kernel assumptions.
- `Mmi386MakeKernelPageTableGlobal` lazily synchronizes missing kernel page tables and is used by the fault path as a fast recovery for kernel PDE misses.
