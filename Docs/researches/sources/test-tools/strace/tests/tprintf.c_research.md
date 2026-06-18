<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/tprintf.c -->
# sources/test-tools/strace/tests/tprintf.c

## Purpose
Covers strace decoder coverage for `tprintf`. Source comments/macros state: Close stdin, move stdout to a non-standard descriptor, and print. Source read: 70 lines, 1192 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <assert.h>, <errno.h>, <stdarg.h>, <stdio.h>, <unistd.h>; defines/undefs: none; C functions: write_loop, tprintf.

## Control Flow
Straight-line fixture code or helper definitions consumed by other tests.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/tprintf.c -->
