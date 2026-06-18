<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/umovestr-illptr.c -->
# sources/test-tools/strace/tests/umovestr-illptr.c

## Purpose
Covers strace decoder coverage for `umovestr-illptr`. Source comments/macros state: Check decoding of invalid pointer by umovestr. Source read: 34 lines, 738 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>, <unistd.h>, "scno.h"; defines/undefs: none; C functions: main; syscall numbers/wrappers: chdir, __NR_chdir.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: chdir, __NR_chdir.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/umovestr-illptr.c -->
