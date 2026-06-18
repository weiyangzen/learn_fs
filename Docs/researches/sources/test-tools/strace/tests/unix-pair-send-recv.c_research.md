<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/unix-pair-send-recv.c -->
# sources/test-tools/strace/tests/unix-pair-send-recv.c

## Purpose
Covers strace decoder coverage for `unix-pair-send-recv`. Source read: 89 lines, 1871 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <assert.h>, <errno.h>, <string.h>, <unistd.h>, <sys/socket.h>, "scno.h"; defines/undefs: __NR_send, SC_send, __NR_recv, SC_recv; C functions: sys_send, sys_recv, transpose, main; syscall numbers/wrappers: send, recv.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations. temporary kernel objects are created to exercise descriptor, timer, or socket decoding. primary syscall coverage: send, recv.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries; creates transient socket state for local decoding.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/unix-pair-send-recv.c -->
