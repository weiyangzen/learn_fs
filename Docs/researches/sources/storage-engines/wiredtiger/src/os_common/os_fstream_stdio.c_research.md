# sources/storage-engines/wiredtiger/src/os_common/os_fstream_stdio.c

## Purpose
Initializes `WT_FSTREAM` wrappers for process stdout and stderr.

## Important APIs, Types, and Functions
`__wt_os_stdio` initializes `WT_STDERR(session)` and `WT_STDOUT(session)` using private `__stdio_init`. Implemented stdio methods are `__stdio_flush` and `__stdio_printf`; close and getline return `ENOTSUP`.

## Control Flow
Initialization stores the stream name and `FILE *`, then installs method pointers. Printing delegates to `vfprintf`; flushing delegates to `fflush`; errors are mapped through `__wt_errno`.

## State and Persistence Behavior
State is the session's stdout/stderr stream wrappers and libc `FILE *` handles. Output is process I/O rather than database persistence.

## Dependencies and Integration Points
The file depends on libc stdio, `WT_FSTREAM`, session stream macros, and WiredTiger error handling. Message and diagnostic output paths use these initialized streams.

## Risks and Edge Cases
Close is unsupported because WiredTiger does not own stdout/stderr. Getline is unsupported. `vfprintf`/`fflush` errors surface as WiredTiger return codes and should not be silently ignored by callers that need reliable output.

## Test Signals
Startup stream initialization, stdout/stderr diagnostic printing, flush failures under redirected/closed descriptors, and unsupported close/getline calls are relevant signals.
