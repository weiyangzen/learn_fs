# sources/test-tools/strace/src/linux/x32/asm_stat.h

## Purpose
Reuses the x86_64 `asm_stat.h` replacement logic for x32 stat structure decoding.

## Important APIs, Types, and Functions
Includes `../x86_64/asm_stat.h`. In x86_64 ILP32 builds, that header temporarily redirects `stat`, includes generic stat definitions, then defines a replacement `struct stat` because older x32 kernel headers were wrong.

## Control Flow and Integration
No runtime flow in this wrapper. The included type definitions are used by `fetch_struct_stat.c`, `fetch_struct_stat64.c`, and old stat decoders.

## State and Persistence
No state; ABI type definitions only.

## Dependencies
Depends on x86_64 stat compatibility logic, `kernel_ulong_t`, and generic asm stat definitions.

## Risks
Stat layouts are ABI-critical. Wrong padding, field width, or header redirection will misdecode `stat`, `lstat`, `fstat`, and related structures for x32.

## Test Signals
x32 stat-family tests should compare decoded fields for device, inode, mode, uid/gid, size, blocks, and timestamps against known fixtures.
