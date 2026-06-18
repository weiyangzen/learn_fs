<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/tampering-notes.c -->
# sources/test-tools/strace/tests/tampering-notes.c

## Purpose
Covers strace decoder coverage for `tampering-notes`. Source comments/macros state: Check tampering notes. Check the return value to pacify the compiler. Source read: 67 lines, 1359 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <limits.h>, <stdio.h>, <stdlib.h>, <string.h>, <unistd.h>; defines/undefs: PATH_LEN; C functions: main; syscall numbers/wrappers: getcwd, __NR_getcwd.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: getcwd, __NR_getcwd.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/tampering-notes.c -->
