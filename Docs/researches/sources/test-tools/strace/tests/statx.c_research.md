<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/statx.c -->
# sources/test-tools/strace/tests/statx.c

## Purpose
Covers strace decoder coverage for `statx`. Source read: 42 lines, 1238 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <linux/stat.h>, "xlat.h", "xlat/statx_masks.h", "xlat/statx_attrs.h", "xlat/at_statx_sync_types.h", "xstatx.c"; defines/undefs: IS_STATX, TEST_SYSCALL_STR, STRUCT_STAT, STRUCT_STAT_STR, STRUCT_STAT_IS_STAT64, TEST_SYSCALL_INVOKE, PRINT_SYSCALL_HEADER, PRINT_SYSCALL_FOOTER; syscall numbers/wrappers: statx, __NR_statx; struct types: statx.

## Control Flow
primary syscall coverage: statx, __NR_statx.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `xlat.h`, Linux UAPI headers, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/statx.c -->
