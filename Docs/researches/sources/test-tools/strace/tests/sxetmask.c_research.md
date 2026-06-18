<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sxetmask.c -->
# sources/test-tools/strace/tests/sxetmask.c

## Purpose
Covers strace decoder coverage for `sxetmask`. Source comments/macros state: Check decoding of sgetmask and ssetmask syscalls. Block, reset, and raise SIGUSR1. If a subsequent ssetmask call fails to set the proper mask, the process will be terminated by SIGUSR1. Use a regular sigprocmask call to check the value returned by the ssetmask call being tested. Source read: 105 lines, 2525 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <errno.h>, <signal.h>, <stdio.h>, <stdint.h>, <string.h>, <unistd.h>; defines/undefs: none; C functions: k_sgetmask, k_ssetmask, main; syscall numbers/wrappers: sgetmask, ssetmask, __NR_sgetmask, __NR_ssetmask.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: sgetmask, ssetmask, __NR_sgetmask, __NR_ssetmask.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sxetmask.c -->
