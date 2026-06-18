<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_pagesize.c -->
# sources/storage-engines/wiredtiger/src/os_posix/os_pagesize.c

## Purpose
Reports the system virtual-memory page size for POSIX builds.

## Important APIs, Types, and Functions
`__wt_get_vm_pagesize(void)` returns `getpagesize()`.

## Control Flow
The function directly calls libc and returns the integer result.

## State and Persistence Behavior
No state is changed. The value influences mmap alignment, allocation assumptions, and page-size-aware hints elsewhere.

## Dependencies and Integration Points
Consumed during connection/platform initialization and by mmap advice alignment logic.

## Risks and Edge Cases
No error handling is present because `getpagesize` is expected to be reliable. Portability depends on the platform exposing it.

## Test Signals
Startup/platform tests should confirm a positive page size and consistency with map alignment assumptions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_pagesize.c -->
