<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/unlink.c -->
# sources/test-tools/strace/tests/unlink.c

## Purpose
Covers strace decoder coverage for `unlink`. Source read: 32 lines, 489 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>; defines/undefs: none; C functions: main; syscall numbers/wrappers: unlink, __NR_unlink.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: unlink, __NR_unlink.

## State And Persistence Behavior
touches temporary filesystem names or descriptors and cleans them through harness/process lifetime.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/unlink.c -->
