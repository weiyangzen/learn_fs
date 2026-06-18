<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getresugid.c -->
# sources/test-tools/strace/tests/getresugid.c

## Purpose
Covers strace decoder coverage for `getresuid`. Source comments describe: Check decoding of getresuid/getresgid/getresuid32/getresgid32 syscalls. Source read: 39 lines, 1054 bytes.

## Important APIs, Types, And Functions
includes/imports: <assert.h>, <stdio.h>, <unistd.h>; defines: none; C functions: main; syscall names/numbers: SYSCALL_NR.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is SYSCALL_NR.

## State And Persistence Behavior
uses tail-allocated buffers to create valid, short-read, and EFAULT-adjacent pointer cases.

## Dependencies And Integration Points
Depends on only the C library/shell runtime and local test harness. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: program stdout contains the canonical expected strace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getresugid.c -->
