<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/strace-n.c -->
# sources/test-tools/strace/tests/strace-n.c

## Purpose
Covers strace command-line option behavior. Source comments/macros state: Test strace's -n option. Source read: 38 lines, 684 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>, <errno.h>; defines/undefs: SC_listen; C functions: main; syscall numbers/wrappers: socketcall, listen, __NR_socketcall, __NR_listen.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: socketcall, listen, __NR_socketcall, __NR_listen.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/strace-n.c -->
