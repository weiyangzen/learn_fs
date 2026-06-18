<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/unblock_reset_raise.c -->
# sources/test-tools/strace/tests/unblock_reset_raise.c

## Purpose
Covers strace decoder coverage for `unblock_reset_raise`. Source comments/macros state: Unblock, reset, and raise a signal. Source read: 34 lines, 746 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <signal.h>, <stdlib.h>, <unistd.h>; defines/undefs: none; C functions: main.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/unblock_reset_raise.c -->
