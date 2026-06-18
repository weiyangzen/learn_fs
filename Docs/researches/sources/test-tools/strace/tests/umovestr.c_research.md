<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/umovestr.c -->
# sources/test-tools/strace/tests/umovestr.c

## Purpose
Covers strace decoder coverage for `umovestr`. Source read: 22 lines, 407 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <string.h>, <unistd.h>; defines/undefs: none; C functions: main.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/umovestr.c -->
