# File Research: sources/windows/reactos/ntoskrnl/mm/i386/page.c

## Purpose

`page.c` is the architecture-level page-table manipulation layer used by the newer ReactOS/ARM3 memory manager for x86-family paging configurations selected through `_MI_PAGING_LEVELS`. It translates memory protections to hardware PTE attributes, creates and deletes virtual mappings, handles pagefile PTEs, queries mapping state, and updates PTE protection/dirty state.

## Main Contents

- Defines `MmProtectToPteMask[32]` and `MmProtectToValue[32]` conversion tables between internal protection masks, Win32 page protections, and hardware PTE flags.
- Implements `MiIsPageTablePresent`, with separate logic for two-level paging and higher-level paging.
- Exposes `MmGetPfnForProcess` for current-process user mappings.
- Implements mapping deletion through `MmDeleteVirtualMappingEx`, wrapped by `MmDeleteVirtualMapping` and `MmDeletePhysicalMapping`.
- Implements pagefile PTE lifecycle through `MmCreatePageFileMapping`, `MmDeletePageFileMapping`, `MmIsPageSwapEntry`, and `MmGetPageFileMapping`.
- Implements mapping lifecycle through `MmCreateVirtualMappingUnsafeEx`, `MmCreateVirtualMappingUnsafe`, `MmCreatePhysicalMapping`, and checked `MmCreateVirtualMapping`.
- Provides query/update helpers: `MmIsPagePresent`, `MmIsDisabledPage`, `MmGetPageProtect`, `MmSetPageProtect`, and `MmSetDirtyBit`.
- Provides no-op `MmInitGlobalKernelPageDirectory` for this implementation and an i386 helper `Mmi386MakeKernelPageTableGlobal`.

## Behavior And Data Flow

User mappings are restricted to the current process and are protected by process working-set locks. Kernel mappings pass `Process == NULL` and must be in system space. `MmCreateVirtualMappingUnsafeEx` ensures the relevant PDE exists, builds a hardware PTE from the supplied protection and PFN, atomically installs it, increments share count for non-physical mappings, and increments page-table references for user mappings. `MmDeleteVirtualMappingEx` atomically clears the PTE, invalidates the TLB entry, optionally returns dirty/PFN information, decrements page-table references, deletes an empty PDE, and decrements the mapped PFN share count for non-physical mappings.

Pagefile mappings encode the swap entry in an invalid PTE shifted left by one. Deleting a pagefile mapping validates that the old PTE is a swap entry, clears it, releases the page-table reference, and returns the original swap entry.

## Concurrency And Invariants

- User-space operations assert `Process == PsGetCurrentProcess()` and acquire working-set locks.
- Kernel-space operations reject user addresses when `Process == NULL`.
- PTE updates use `InterlockedExchangePte` and flush with `KeInvalidateTlbEntry` when a valid or changed mapping may be cached.
- Page-table reference accounting controls when empty user PDEs can be deleted.
- PFN share-count updates are protected by the PFN lock.

## Notable Details

- `MmSetPageProtect` allows restoring access from `PAGE_NOACCESS` as long as the invalid PTE still contains a PFN and is not a swap entry.
- `MmIsDisabledPage` identifies invalid, non-swap PTEs with a nonzero page frame, representing a protection-disabled resident page.
- Write-copy protections are rejected for legacy kernel mappings in `MmCreateVirtualMappingUnsafeEx`.
- The implementation has strong current-process assumptions and is not a general cross-process page-table editor.
