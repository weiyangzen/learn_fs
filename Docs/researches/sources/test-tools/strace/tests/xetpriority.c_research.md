<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/xetpriority.c -->
# sources/test-tools/strace/tests/xetpriority.c

## Purpose
Covers strace decoder coverage for `xetpriority`. Source comments/macros state: Check decoding of getpriority and setpriority syscalls. Source read: 47 lines, 1075 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "pidns.h", <stdio.h>, <sys/resource.h>, <unistd.h>; defines/undefs: none; C functions: main; syscall numbers/wrappers: getpriority, setpriority, __NR_getpriority, __NR_setpriority.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: getpriority, setpriority, __NR_getpriority, __NR_setpriority.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `pidns.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; pid namespace translation depends on namespace support and synchronization. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/xetpriority.c -->
