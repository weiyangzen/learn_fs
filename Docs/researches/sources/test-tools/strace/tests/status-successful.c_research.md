<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/status-successful.c -->
# sources/test-tools/strace/tests/status-successful.c

## Purpose
Covers strace status filtering and status-summary behavior. Source comments/macros state: Check status=successful filtering for failed and successful syscalls. Source read: 24 lines, 525 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>; defines/undefs: none; C functions: main.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/status-successful.c -->
