<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/vmsplice.c -->
# sources/test-tools/strace/tests/vmsplice.c

## Purpose
Covers strace decoder coverage for `vmsplice`. Source comments/macros state: Check decoding of vmsplice syscall. Source read: 80 lines, 1964 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <assert.h>, <stdio.h>, <unistd.h>, <sys/uio.h>; defines/undefs: none; C functions: main; syscall numbers/wrappers: vmsplice, __NR_vmsplice; struct types: iovec.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. temporary kernel objects are created to exercise descriptor, timer, or socket decoding. primary syscall coverage: vmsplice, __NR_vmsplice.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/vmsplice.c -->
