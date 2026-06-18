<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/xet_robust_list.c -->
# sources/test-tools/strace/tests/xet_robust_list.c

## Purpose
Covers strace decoder coverage for `xet_robust_list`. Source comments/macros state: Check decoding of get_robust_list and set_robust_list syscalls. It has dual-use as a marker of the beginning of the test output Source read: 71 lines, 1839 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "pidns.h", <stdio.h>, <unistd.h>; defines/undefs: none; C functions: sprintaddr, main; syscall numbers/wrappers: get_robust_list, set_robust_list, __NR_get_robust_list, __NR_set_robust_list.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: get_robust_list, set_robust_list, __NR_get_robust_list, __NR_set_robust_list.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `pidns.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; pid namespace translation depends on namespace support and synchronization. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/xet_robust_list.c -->
