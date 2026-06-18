<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/umask.c -->
# sources/test-tools/strace/tests/umask.c

## Purpose
Covers strace decoder coverage for `umask`. Source read: 31 lines, 513 bytes.

## Important APIs, Types, And Functions
includes/imports: <stdio.h>, <sys/stat.h>; defines/undefs: none; C functions: test_umask, main.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on the C library/shell runtime and local strace test harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/umask.c -->
