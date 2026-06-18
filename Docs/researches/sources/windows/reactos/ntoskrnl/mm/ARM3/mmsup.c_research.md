# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/mmsup.c

## Role

`mmsup.c` contains small ARM3 memory-manager support routines exposed through NT MM APIs. It mixes implemented query/validation helpers with several unimplemented public stubs.

## Key mechanisms

- Defines working-set global counters: `MmMinimumWorkingSetSize`, `MmMaximumWorkingSetSize`, and `MmPagesAboveWsMinimum`.
- `MmAdjustWorkingSetSize` handles the normal resizing path for the current process working set. It locks the process `Vm` working set, derives requested min/max page counts, clamps to global min/max, rejects min greater than max, checks privilege/resource conditions for increases, updates resident available pages and global pages-above-minimum accounting, and writes the new process working-set bounds.
- `MmIsAddressValid` walks the paging hierarchy according to `_MI_PAGING_LEVELS`: PXE, PPE, PDE, then PTE. It returns false on any invalid level and true only when the final PTE is valid. The comment warns the result remains stable only if the caller holds the PFN lock.
- `MmIsNonPagedSystemAddressValid` warns that it returns a bogus result and delegates to `MmIsAddressValid`.
- `MmIsRecursiveIoFault` checks thread flags `DisablePageFaultClustering` and `ForwardClusterOnly`.
- `MmIsThisAnNtAsSystem` returns whether `MmProductType` indicates a server system; `MmQuerySystemSize` returns `MmSystemSize`.
- Stubbed/unimplemented routines include `MmMapUserAddressesToPage`, the working-set emptying special case in `MmAdjustWorkingSetSize`, `MmSetAddressRangeModified`, `MmSetBankedSection`, and `MmCreateMirror`.

## Dependencies and coupling

- Includes `miarm.h` for working-set lock helpers and page-table address helpers.
- Uses `PsGetCurrentProcess`, `PsGetCurrentThread`, thread flags, process `Vm`, and global available/resident/system-lock page counters initialized or tuned elsewhere.
- Uses `MmProductType` and `MmSystemSize` initialized in `mminit.c`.

## Limitations and risks

- Multiple public APIs are stubs returning `STATUS_NOT_IMPLEMENTED` or `FALSE`.
- `MmIsNonPagedSystemAddressValid` explicitly logs that its result is not trustworthy.
- `MmIsAddressValid` is a snapshot check; callers that need stability must hold the PFN lock or otherwise prevent invalidation.
