<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/swap.c -->
# sources/test-tools/strace/tests/swap.c

## Purpose
Covers strace decoder coverage for `swap`. Source comments/macros state: Check decoding of swapon and swapoff tests. Source read: 52 lines, 1264 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <sys/swap.h>, <unistd.h>; defines/undefs: none; C functions: main; syscall numbers/wrappers: swapon, swapoff, __NR_swapon, __NR_swapoff.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: swapon, swapoff, __NR_swapon, __NR_swapoff.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/swap.c -->
