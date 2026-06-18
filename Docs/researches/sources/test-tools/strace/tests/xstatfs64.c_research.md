<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/xstatfs64.c -->
# sources/test-tools/strace/tests/xstatfs64.c

## Purpose
Covers strace decoder coverage for `xstatfs64`. Source read: 28 lines, 785 bytes.

## Important APIs, Types, And Functions
includes/imports: "xstatfsx.c"; defines/undefs: SYSCALL_INVOKE, PRINT_SYSCALL_HEADER, STRUCT_STATFS, PRINT_F_FRSIZE, PRINT_F_FLAGS, PRINT_F_FSID, CHECK_ODD_SIZE; syscall numbers/wrappers: SYSCALL_NR; struct types: statfs64.

## Control Flow
primary syscall coverage: SYSCALL_NR.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on the C library/shell runtime and local strace test harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/xstatfs64.c -->
