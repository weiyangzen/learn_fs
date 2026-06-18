<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/futex_wake.c -->
# sources/test-tools/strace/tests/futex_wake.c

## Purpose
Covers strace decoder coverage for `futex_wake`. Source comments describe: Check decoding of futex_wake syscall. FUTEX_BITSET_MATCH_ANY Source read: 97 lines, 2047 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "futex2_flags.h", "scno.h", "xmalloc.h", <stdio.h>, <unistd.h>; defines: none; C functions: k_futex_wake, main; syscall names/numbers: futex_wake, __NR_futex_wake.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. small syscall wrapper helpers OR high filler bits into integer arguments so strace's decoding and truncation paths are exercised. nested loops cover flag, pointer, size, fd, and translation-mode combinations. primary syscall coverage is futex_wake, __NR_futex_wake.

## State And Persistence Behavior
uses tail-allocated buffers to create valid, short-read, and EFAULT-adjacent pointer cases.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `xmalloc.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling; expected output depends on xlat raw/abbrev/verbose formatting. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/futex_wake.c -->
