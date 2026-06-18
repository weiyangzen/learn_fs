<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/umovestr2.c -->
# sources/test-tools/strace/tests/umovestr2.c

## Purpose
Covers strace decoder coverage for `umovestr2`. Source read: 33 lines, 657 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>, <string.h>, <unistd.h>; defines/undefs: none; C functions: main.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/umovestr2.c -->
