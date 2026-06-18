# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/largepag.c

## Purpose

`largepag.c` contains ARM3 large-page support scaffolding. In this snapshot, large-page support is mostly unimplemented, but the file initializes related global state, a process tracking list, and driver large-page configuration parsing.

## Main State

- `MmProcessList` tracks processes for large-page-related handling.
- `MiLargePageHyperPte` reserves a system PTE used for initial large-page mapping support.
- `MiLargePageRangeIndex` and `MiLargePageRanges[64]` store cached large-page ranges.
- `MmLargePageDriverBuffer[512]` and `MmLargePageDriverBufferLength` hold configured driver names.
- `MiLargePageDriverList` stores parsed driver entries.
- `MiLargePageAllDrivers` enables all drivers when the buffer contains `*`.

## Initialization

`MiInitializeLargePageSupport`:

- on PAE/x64-style paging levels (`_MI_PAGING_LEVELS > 2`), prints that the path is not implemented
- otherwise reserves one system PTE from `SystemPteSpace` for `MiLargePageHyperPte`
- clears that PTE
- initializes `MmProcessList`
- inserts the current process into the process list

## Cached Range Sync

`MiSyncCachedRanges` loops over `MiLargePageRanges` up to `MiLargePageRangeIndex`, but each entry currently triggers `UNIMPLEMENTED_DBGBREAK("No support for large pages")`.

## Driver List Parsing

`MiInitializeDriverLargePageList`:

- initializes `MiLargePageDriverList`
- exits if `MmLargePageDriverBufferLength == 0xFFFFFFFF`
- scans the configured wide-character buffer
- skips whitespace
- treats `*` as "all drivers" and sets `MiLargePageAllDrivers`
- otherwise prints that large page drivers are unsupported and asserts

## Notable Details

- Large-page support is effectively placeholder code in this file.
- The only non-stubbed successful path is initialization of the reserved PTE and process list on two-level paging.
- Explicit driver names are not supported; only the wildcard case is accepted without assertion.
