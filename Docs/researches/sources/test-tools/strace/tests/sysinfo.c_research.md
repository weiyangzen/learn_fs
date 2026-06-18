<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sysinfo.c -->
# sources/test-tools/strace/tests/sysinfo.c

## Purpose
Covers strace decoder coverage for `sysinfo`. Source comments/macros state: This file is part of sysinfo strace test. Source read: 57 lines, 1356 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>, <sys/sysinfo.h>; defines/undefs: none; C functions: main; struct types: sysinfo.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sysinfo.c -->
