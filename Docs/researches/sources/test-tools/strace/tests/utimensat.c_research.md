<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/utimensat.c -->
# sources/test-tools/strace/tests/utimensat.c

## Purpose
Covers strace decoder coverage for `utimensat`. Source comments/macros state: Check decoding of utimensat syscall. AT_FDCWD AT_SYMLINK_NOFOLLOW AT_REMOVEDIR AT_REMOVEDIR|AT_SYMLINK_FOLLOW AT_SYMLINK_NOFOLLOW|AT_REMOVEDIR|AT_SYMLINK_FOLLOW" \ "|AT_NO_AUTOMOUNT|AT_EMPTY_PATH|AT_RECURSIVE|0xffff60ff UTIME_NOW UTIME_OMIT dirfd pathname times flags Source read: 227 lines, 7026 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <fcntl.h>, <stdint.h>, <stdio.h>, <sys/stat.h>, <sys/time.h>, <unistd.h>, "scno.h"; defines/undefs: big_tv_sec, huge_tv_sec, str_at_fdcwd, str_at_symlink_nofollow, str_at_removedir, str_flags1, str_flags2, str_utime_now_omit; C functions: print_ts, k_utimensat, main; syscall numbers/wrappers: utimensat, __NR_utimensat.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: utimensat, __NR_utimensat.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries; observes or mutates time/timer state only inside the test process or temporary file.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; expected output is sensitive to xlat and string-escaping mode; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/utimensat.c -->
