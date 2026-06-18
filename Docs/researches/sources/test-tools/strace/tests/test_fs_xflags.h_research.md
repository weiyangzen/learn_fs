<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/test_fs_xflags.h -->
# sources/test-tools/strace/tests/test_fs_xflags.h

## Purpose
Covers shared strace test helper definitions for `test_fs_xflags`. Source read: 30 lines, 750 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines/undefs: VALID_FS_XFLAGS, INVALID_FS_XFLAGS, INVALID_FS_XFLAGS64, VALID_FS_XFLAGS_STR, INVALID_FS_XFLAGS_STR.

## Control Flow
Straight-line fixture code or helper definitions consumed by other tests.

## State And Persistence Behavior
No independent runtime state is owned here; including tests receive compile-time constants, macros, inline helpers, and declarations.

## Dependencies And Integration Points
Depends on the C library/shell runtime and local strace test harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: signals are compile success and behavior of including tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/test_fs_xflags.h -->
