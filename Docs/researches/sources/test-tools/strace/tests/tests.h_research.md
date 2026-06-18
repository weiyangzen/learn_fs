<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/tests.h -->
# sources/test-tools/strace/tests/tests.h

## Purpose
Covers shared strace test helper definitions for `tests`. Source comments/macros state: Tests of "strace -v" are expected to define VERBOSE to 1. xlat verbosity defaults " str_ " " dflt_ " " str_ " " dflt_ " %s %s %s %s %s %s !XLAT_RAW && !XLAT_VERBOSE " dflt_ " " dflt_ " XLAT_RAW, XLAT_VERBOSE Default maximum # of bytes printed in printstr et al. Cached sysconf(_SC_PAGESIZE). The size of kernel's sigset_t. Print message and strerror(errno) to stderr, then exit(1). Print message to stderr, then. Source read: 522 lines, 16179 bytes.

## Important APIs, Types, And Functions
includes/imports: "config.h", <stdbool.h>, <stdint.h>, <sys/types.h>, "kernel_types.h", "kernel_old_timespec.h", "gcc_compat.h", "macros.h"; defines/undefs: STRACE_TESTS_H, SIZEOF_KERNEL_LONG_T, SIZEOF_LONG, VERBOSE, XLAT_RAW, XLAT_VERBOSE, XLAT_name, XLAT_KNOWN, XLAT_UNKNOWN, XLAT_KNOWN_FMT, XLAT_UNKNOWN_FMT, XLAT_FMT, XLAT_FMT_D, XLAT_FMT_JD, XLAT_FMT_U, XLAT_FMT_L, XLAT_FMT_LL, XLAT_ARGS, XLAT_ARGS_U, XLAT_SEL, ABBR, RAW, VERB, NABBR, NRAW, NVERB, XLAT_STR, ARG_XLAT_KNOWN; C functions: get_page_size, get_sigset_size, perror_msg_and_fail, error_msg_and_fail, error_msg_and_skip, perror_msg_and_skip, skip_if_unavailable, get_dir_fd, create_and_enter_subdir, leave_and_remove_subdir, lock_file_by_dirname, fill_memory_ex, fill_memory, fill_memory16_ex, fill_memory16, fill_memory32_ex, fill_memory32, fill_memory64_ex, fill_memory64, tprintf, inode_of_sockfd, print_quoted_string_ex, print_quoted_string, print_quoted_cstring, print_quoted_stringn, print_quoted_memory_ex, print_quoted_memory, print_quoted_hex, print_time_t_nsec, print_time_t_usec; syscall numbers/wrappers: socketcall; struct types: strval8, strval16, strval32, strival32, strval_klong, strval64, xlat, mmsghdr; harness commands: void check_overflowuid(const int);, void check_overflowgid(const int);.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: socketcall.

## State And Persistence Behavior
No independent runtime state is owned here; including tests receive compile-time constants, macros, inline helpers, and declarations.

## Dependencies And Integration Points
Depends on configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; expected output is sensitive to xlat and string-escaping mode; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail; harness performs regex/grep matching; signals are compile success and behavior of including tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/tests.h -->
