<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/subdir.c -->
# sources/test-tools/strace/tests/subdir.c

## Purpose
Covers strace decoder coverage for `subdir`. Source read: 40 lines, 745 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <dirent.h>, <unistd.h>, <sys/stat.h>; defines/undefs: none; C functions: create_and_enter_subdir, leave_and_remove_subdir.

## Control Flow
Straight-line fixture code or helper definitions consumed by other tests.

## State And Persistence Behavior
touches temporary filesystem names or descriptors and cleans them through harness/process lifetime.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/subdir.c -->
