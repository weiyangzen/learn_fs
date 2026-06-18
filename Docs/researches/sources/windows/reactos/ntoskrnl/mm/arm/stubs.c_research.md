# File Research: sources/windows/reactos/ntoskrnl/mm/arm/stubs.c

## Role In Subset

Provides a partial older ARM memory-manager implementation: page-table lookup/creation, kernel virtual mapping creation/deletion, process page-directory creation, basic PFN lookup/presence checks, kernel page-directory initialization, and ARM physical-address lookup.

## Main Responsibilities

- Maintains `MmGlobalKernelPageDirectory`, `MiArmTemplatePte`, and `MiArmTemplatePde`.
- `MiGetPageTableForProcess` locates or creates coarse page tables for addresses, allocating nonpaged-pool pages as needed.
- `MmCreateProcessAddressSpace` allocates page-directory/hyperspace pages, copies kernel PDEs, and sets recursive/hyperspace PDEs.
- `MmCreateVirtualMappingInternal` writes ARM PTEs over a range, creating page tables when crossing PDE boundaries.
- `MmCreateVirtualMapping` validates pages are in use, then delegates to the unsafe/internal mapping path.
- `MmDeleteVirtualMapping` clears a PTE, flushes TLB, returns PFN, and reports dirty state as false.
- `MmGetPfnForProcess`, `MmIsPagePresent`, and `MmIsPageSwapEntry` inspect captured PTEs.
- `MmInitGlobalKernelPageDirectory` captures template PTE/PDE values from a known-good kernel mapping and records kernel PDEs.
- `MmGetPhysicalAddress` handles a special early PCR section mapping and normal valid PTE lookup.

## Locking And Architecture Behavior

- Uses ARM-specific `KeArmInvalidateTlbEntry`.
- Uses hyperspace mappings while constructing a process page directory.
- Kernel mappings are supported more directly than user mappings.
- Page table unmapping for user-mode paths is effectively fatal/unsupported.

## Notable Limitations

- User-mode memory support is explicitly marked unsupported in several paths.
- Some control flow uses a `kernelHack` path for page-table creation.
- Dirty page operations and pagefile mapping operations are unimplemented.
- `MmDeleteVirtualMapping` reports `WasDirty = FALSE` with an explicit “LIE” comment.
- The code references `FreePage` in deletion logic, implying reliance on external/global behavior not visible in this file.
- Protection is not enforced and returns read/write behavior.

## Filesystem-Relevant Notes

This partial ARM implementation could support simple kernel mappings but is not sufficient for full filesystem paging behavior: dirty tracking, pagefile mappings, user mapped views, and protection enforcement are incomplete.
