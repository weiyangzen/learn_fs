<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/umovestr3.c -->
# sources/test-tools/strace/tests/umovestr3.c

## Purpose
Covers strace decoder coverage for `umovestr3`. Source read: 28 lines, 545 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <limits.h>, <stdio.h>, <unistd.h>; defines/undefs: none; C functions: main.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/umovestr3.c -->
