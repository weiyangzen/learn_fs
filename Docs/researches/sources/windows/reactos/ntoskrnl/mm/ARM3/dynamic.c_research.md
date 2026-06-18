# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/dynamic.c

Read status: complete file, 126 lines.

This file provides the ARM3 dynamic physical-memory API surface. Hot-add, hot-remove, and bad/good marking APIs are stubs; physical memory range enumeration is implemented.

Key entry points:
- `MmAddPhysicalMemory()`, `MmMarkPhysicalMemoryAsBad()`, `MmMarkPhysicalMemoryAsGood()`, and `MmRemovePhysicalMemory()` are unimplemented and return `STATUS_NOT_IMPLEMENTED`.
- `MmGetPhysicalMemoryRanges()` allocates a nonpaged copy of `MmPhysicalMemoryBlock` runs as byte-based `PHYSICAL_MEMORY_RANGE` entries, appends a zero terminator, and returns it to the caller.

Important dependencies:
- `MmPhysicalMemoryBlock` run metadata.
- PFN lock routines `MiAcquirePfnLock()` and `MiReleasePfnLock()`.
- Nonpaged pool tag `'hPmM'`.

Notable behavior:
- `MmGetPhysicalMemoryRanges()` asserts PASSIVE_LEVEL, sizes the buffer from `NumberOfRuns + 1`, and asserts the run count did not change after acquiring the PFN lock.
- Returned ranges convert pages to bytes with `<< PAGE_SHIFT` and require caller-side pool freeing.
- Dynamic physical memory mutation is not supported by this implementation.
