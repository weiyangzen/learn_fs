# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/internal.h

## Purpose
`internal.h` supplies small private declarations for com_err implementation files.

## Important APIs, Types, and Functions
It includes `errno.h` and conditionally declares `sys_errlist` and `sys_nerr` when `NEED_SYS_ERRLIST` is configured.

## Control Flow
There is no runtime control flow.

## State, Persistence, Dependencies, Risks, and Test Signals
State is limited to external libc globals when needed. Dependencies are platform C library errno support. Risks are portability issues on systems where `sys_errlist` is hidden or has incompatible constness. Test signals are successful compilation of `error_message.c` on configured legacy platforms.
