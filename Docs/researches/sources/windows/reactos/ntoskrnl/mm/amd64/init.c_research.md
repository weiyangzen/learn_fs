# File Research: sources/windows/reactos/ntoskrnl/mm/amd64/init.c

## Role In Subset

Provides amd64 machine-dependent memory-manager initialization for ReactOS ARM3: template PTE/PDE setup, session/system VA layout, early page-table construction, nonpaged pool/system PTE layout, PFN database mapping/population, and final machine-dependent initialization.

## Main Responsibilities

- Defines amd64 kernel PTE/PDE templates: valid kernel, local kernel, demand-zero, prototype, and decommitted PTEs.
- Builds session, session image, session working set, session view, session pool, and system view layout in `MiInitializeSessionSpaceLayout`.
- Maps paging hierarchy levels with `MiMapPPEs`, `MiMapPDEs`, and `MiMapPTEs`.
- Initializes the active page table in `MiInitializePageTable`, clears user PXEs, enables global pages, sets hyperspace, debug mapping, mapping range, VAD bitmap, and working-set-list mappings.
- Calculates and maps nonpaged pool in `MiBuildNonPagedPool`.
- Creates system PTE space and reserves zeroing PTEs in `MiBuildSystemPteSpace`.
- Maps and initializes the PFN database with `MiBuildPfnDatabase`, using loader memory descriptors and page-table walks.
- Completes amd64 MM bring-up in `MiInitMachineDependent`.

## PFN Database Details

- `MiAddDescriptorToDatabase` adds free memory to the free list, marks XIP ROM specially, asserts on bad memory, and marks other memory active.
- `MiBuildPfnDatabaseFromPageTables` walks valid paging structures and calls `MiSetupPfnForPageTable` so PFN entries reflect existing boot mappings.
- The initializer temporarily consumes boot allocator pages through `MxGetNextPage`, then reconstructs accounting from loader descriptors.

## Notable Limitations

- Nonpaged pool percentage registry cap is unimplemented.
- Some page-zeroing and global-page comments are marked TODO/FIXME.
- Loader bad memory currently asserts.
- Cache attribute setup has a FIXME noting mismatch with Windows expectations.
- Several ref/share counts are manually reset after PFN database construction so process address-space initialization can proceed.

## Filesystem-Relevant Notes

This file establishes the kernel virtual address regions used later by cache manager, system PTE mappings, nonpaged pool allocations, and PFN accounting. Filesystem and block I/O paths depend on these regions being initialized before mapped I/O, MDLs, and cache trimming are reliable.
