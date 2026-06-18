# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/i386/init.c

## Purpose

`i386/init.c` contains x86-specific ARM3 memory-manager initialization. It defines hardware/software PTE templates, computes session and nonpaged-pool layout, builds early kernel paging structures, initializes nonpaged pool and system PTE space, creates hyperspace, reserves zeroing PTEs, and completes initial process address-space setup.

## PTE/PDE Templates

The file defines architecture templates:

- `ValidKernelPde`
- `ValidKernelPte`
- `ValidKernelPdeLocal`
- `ValidKernelPteLocal`
- `DemandZeroPde`
- `DemandZeroPte`
- `PrototypePte`
- `MmDecommittedPte`

The valid templates use x86 present/read-write/dirty/accessed bits. A disabled global-page block can set global bits when supported.

## Session Layout

`MiInitializeSessionSpaceLayout` computes session-related virtual ranges:

- session size
- session view size
- session pool size
- session image size
- system view size
- session image start/end
- session view start
- session pool start/end
- session base and end
- system view start
- PTE pointers for the session regions
- `MmSessionSpace` placement near the session image area

It asserts that `MmSessionBase + MmSessionSize == PTE_BASE`.

## Nonpaged Pool Sizing

`MiComputeNonPagedPoolVa` tunes initial and maximum nonpaged pool sizes from free physical pages and registry-derived globals.

Important behavior:

- forces 2 MB initial nonpaged pool on very small systems when no override exists
- rejects an initial pool larger than 7/8 of free RAM
- computes a dynamic initial size from a minimum plus per-MB additions
- caps initial size at `MI_MAX_INIT_NONPAGED_POOL_SIZE`
- computes maximum size including PFN database space
- increases maximum pool for larger-memory machines
- ensures maximum covers initial pool, PFN database, and expansion slack
- caps the architectural maximum at twice `MI_MAX_NONPAGED_POOL_SIZE`
- restricts the extra high-memory boost when expansion is assumed unavailable

Percentage-based maximum nonpaged pool configuration is marked `UNIMPLEMENTED`.

## Machine-Dependent Initialization

`MiInitMachineDependent` performs the core x86 ARM3 boot memory setup:

- sets the system process CR3 from the PDE base mapping
- clears user-mode PDEs
- computes nonpaged pool size and expansion VA
- places the shadow PFN database at `0xB0000000`
- places system PTE space in the loader gap after `KSEG0_BASE + MmBootImageSize`
- computes `MmNumberOfSystemPtes`
- maps page tables for system PTE space
- maps page tables for nonpaged pool expansion
- maps page tables for the PFN database and initial nonpaged pool
- obtains contiguous physical pages for the PFN database and initial nonpaged pool
- maps initial nonpaged pool PTEs
- initializes nonpaged pool thresholds, PFN database, color tables, and the balancer
- restores the loader free descriptor
- calls `InitializePool(NonPagedPool, 0)`
- initializes the system PTE allocator with `MiInitializeSystemPtes`
- creates hyperspace PDE/page table and stores the hyperspace page-table frame in `DirectoryTableBase[1]`
- initializes the reserved hyperspace mapping counter
- reserves zeroing PTEs and initializes their counter
- maps and zeros the working set list page
- applies the Pentium F00F errata write-through workaround to the IDT page when needed
- initializes the process address space for the current process
- validates color-list mappings and initializes PFN metadata for color-list pages

## Hyperspace and Zeroing Integration

This file initializes the globals consumed by `hypermap.c`:

- `MmFirstReservedMappingPte`
- `MmLastReservedMappingPte`
- `MiFirstReservedZeroingPte`

It also initializes `MmWorkingSetList` and the current process working set page.

## Notable Details

- The PFN database is described as a temporary "Shadow PFN Database" to coexist with the old memory manager.
- `MmNonPagedSystemStart` is kept initialized for debugger use even though system PTE space is placed in a loader-gap region.
- Several calculations are protected by assertions that ensure no virtual address overlap between loader mappings, system PTEs, PFN database, and nonpaged pool.
- PAE/x64-specific paths are not handled in this file; it is the i386 initialization path.
