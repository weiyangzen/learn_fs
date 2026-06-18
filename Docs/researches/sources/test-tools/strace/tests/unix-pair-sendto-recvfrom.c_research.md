<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/unix-pair-sendto-recvfrom.c -->
# sources/test-tools/strace/tests/unix-pair-sendto-recvfrom.c

## Purpose
Covers strace decoder coverage for `unix-pair-sendto-recvfrom`. Source comments/macros state: Check decoding and dumping of sendto and recvfrom syscalls. Source read: 66 lines, 1432 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <assert.h>, <string.h>, <unistd.h>, <sys/socket.h>, <sys/wait.h>; defines/undefs: none; C functions: transpose, main.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations. process/thread branches synchronize children or threads before final trace comparison. temporary kernel objects are created to exercise descriptor, timer, or socket decoding.

## State And Persistence Behavior
creates transient socket state for local decoding; owns transient child/thread lifecycle state that must be synchronized before exit.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: process/thread ordering can make trace matching fragile. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/unix-pair-sendto-recvfrom.c -->
