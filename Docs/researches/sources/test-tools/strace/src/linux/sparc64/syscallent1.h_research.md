# sources/test-tools/strace/src/linux/sparc64/syscallent1.h

## Purpose
Provides the secondary SPARC64 personality syscall table by including `../sparc/syscallent.h`. In strace's multi-personality builds this represents the 32-bit SPARC personality traced by a SPARC64 build.

## Important APIs, Types, and Functions
Exports no functions or local definitions. Its only API surface is the include indirection that lets `syscall.c` build `sysent1` when `SUPPORTED_PERSONALITIES > 1`.

## Control Flow and Integration
Compile-time inclusion pulls in the SPARC 32-bit syscall initializer rows. Runtime personality selection in `syscall.c` and architecture code determines whether the table from this file or the primary `sparc64/syscallent.h` table is used.

## State and Persistence
No local state. The compiled result is a static syscall metadata table for the 32-bit SPARC personality.

## Dependencies
Depends entirely on `sources/test-tools/strace/src/linux/sparc/syscallent.h` and on the multi-personality table logic in `syscall.c`.

## Risks
The risk is mostly ABI routing: if SPARC64 personality detection chooses this table incorrectly, syscall names and argument widths will be wrong. Changes to the included SPARC table automatically affect SPARC64 compat tracing.

## Test Signals
Look for successful multi-personality SPARC64 builds and traces from 32-bit SPARC processes under a 64-bit tracer. Filter syntax using the secondary personality should resolve syscall names from the included SPARC table.
