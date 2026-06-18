<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_pagesize.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_pagesize.c

## Purpose
Reports Windows virtual-memory page size.

## Important APIs, Types, and Functions
`__wt_get_vm_pagesize` calls `GetSystemInfo` and returns `dwPageSize`.

## Control Flow
The function fills a `SYSTEM_INFO` structure and returns the page-size field.

## State and Persistence Behavior
No state changes. The result is used for memory mapping and page-aligned operations.

## Dependencies and Integration Points
Used by platform initialization and mapping helpers that need page-size alignment.

## Risks and Edge Cases
Assumes `dwPageSize` fits in `int`, which is true for normal Windows systems.

## Test Signals
Startup tests should validate a positive page size and consistency with allocation granularity assumptions where relevant.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_pagesize.c -->
