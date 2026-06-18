<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/uname.c -->
# sources/test-tools/strace/tests/uname.c

## Purpose
Covers strace decoder coverage for `uname`. Source comments/macros state: Check decoding of uname syscall. Source read: 44 lines, 966 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <sys/utsname.h>, <unistd.h>; defines/undefs: none; C functions: main; syscall numbers/wrappers: uname, __NR_uname; struct types: utsname.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: uname, __NR_uname.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/uname.c -->
