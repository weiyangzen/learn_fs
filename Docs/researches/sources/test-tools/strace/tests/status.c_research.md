<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/status.c -->
# sources/test-tools/strace/tests/status.c

## Purpose
Covers strace status filtering and status-summary behavior. Source comments/macros state: Helper function to check -e status option. Source read: 21 lines, 509 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>, <unistd.h>; defines/undefs: none; C functions: test_status_chdir.

## Control Flow
Straight-line fixture code or helper definitions consumed by other tests.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/status.c -->
