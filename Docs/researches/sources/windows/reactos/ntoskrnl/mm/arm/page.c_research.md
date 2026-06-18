# File Research: sources/windows/reactos/ntoskrnl/mm/arm/page.c

## Role In Subset

Contains an older ARM page-management file with protection translation tables and mostly placeholder implementations for legacy page mapping APIs.

## Main Responsibilities

- Defines ARM `MmProtectToPteMask` and `MmProtectToValue` arrays mapping internal MM protections to PTE bits and Win32 protection constants.
- Defines `MmGlobalKernelPageDirectory`, kernel/demand-zero/prototype/decommitted PTE templates, and local kernel templates.
- Provides `MmInitGlobalKernelPageDirectory`, which records existing kernel PDEs while skipping recursive PTE and hyperspace slots.
- Provides trivial protection getter/setter behavior, returning read/write and ignoring requested changes.
- Declares stubs for process address-space creation, virtual mapping creation/deletion, pagefile mapping, PFN lookup, dirty state, presence checks, swap entry checks, disabled page checks, and session-space layout.

## Notable Limitations

- Most operational functions call `UNIMPLEMENTED_DBGBREAK`, return false/success placeholders, or assert.
- Page protection is not enforced; pages are treated as RWX/read-write by the exposed helpers.
- `MmGetPageFileMapping`, `MmIsDisabledPage`, and `MiInitializeSessionSpaceLayout` assert false.
- This file is less complete than `arm/stubs.c` and appears to be a placeholder ARM path.

## Filesystem-Relevant Notes

The file does not provide a production-grade ARM memory mapping substrate. Any filesystem or cache behavior requiring ARM pagefile mappings, dirty tracking, or robust virtual mapping would depend on unimplemented functionality here.
