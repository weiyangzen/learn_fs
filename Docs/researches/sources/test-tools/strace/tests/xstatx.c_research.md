<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/xstatx.c -->
# sources/test-tools/strace/tests/xstatx.c

## Purpose
Covers strace decoder coverage for `xstatx`. Source comments/macros state: MPERS_IS_m32 || MPERS_IS_mx32 || HAVE_STRUCT_STAT64_ST_MTIME_NSEC !STRUCT_STAT_IS_STAT64 MPERS_IS_m32 || MPERS_IS_mx32 STRUCT_STAT_IS_STAT64 Fixes -Wunused warning ", mode); print_ftype(mode); printf("|"); print_perms(mode); printf(" makedev(%#x, %#x) XLAT_ABBREV !OLD_STAT OLD_STAT !IS_STATX !IS_STATX !OLD_STAT IS_STATX We're done playing with flags. STATX_??? ...and with mask. IS_STATX error TEST_SYSCALL_STR must. Source read: 550 lines, 13885 bytes.

## Important APIs, Types, And Functions
includes/imports: <errno.h>, <stdio.h>, <stddef.h>, <time.h>, <unistd.h>, <sys/sysmacros.h>, "print_fields.h", <fcntl.h>, <sys/stat.h>, "asm_stat.h"; defines/undefs: STRUCT_STAT, STRUCT_STAT_STR, STRUCT_STAT_IS_STAT64, SAMPLE_SIZE, stat, stat64, statx, statx_timestamp, st_atime, st_mtime, st_ctime, HAVE_STRUCT_STAT_ST_MTIME_NSEC, TEST_BOGUS_STRUCT_STAT, IS_FSTAT, OLD_STAT, IS_STATX, TIME_NSEC, HAVE_NSEC, PRINT_ST_TIME, PRINT_FIELD_U32_UID, PRINT_FIELD_TIME, ST_SIZE_FIELD, LOG_STAT_OFFSETOF_SIZEOF, INVOKE, SET_FLAGS_INVOKE, SET_MASK_INVOKE; C functions: print_ftype, print_perms, print_st_mode, sprint_makedev, print_stat, create_sample, main; struct types: stat, statx, timespec.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries; touches temporary filesystem names or descriptors and cleans them through harness/process lifetime.

## Dependencies And Integration Points
Depends on procfs. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: expected output is sensitive to xlat and string-escaping mode; kernel configuration, procfs visibility, or privileges can change availability; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/xstatx.c -->
