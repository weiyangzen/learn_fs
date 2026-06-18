<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/xgetdents.c -->
# sources/test-tools/strace/tests/xgetdents.c

## Purpose
Covers strace decoder coverage for `xgetdents`. Source comments/macros state: Check decoding of getdents and getdents64 syscalls. %lu entries 0 entries Source read: 141 lines, 3310 bytes.

## Important APIs, Types, And Functions
includes/imports: <dirent.h>, <fcntl.h>, <stdio.h>, <unistd.h>, <sys/stat.h>, "kernel_dirent.h", "print_fields.h"; defines/undefs: none; C functions: str_d_type, print_dirent, k_getdents, ls, main; syscall numbers/wrappers: NR_getdents.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations. primary syscall coverage: NR_getdents.

## State And Persistence Behavior
touches temporary filesystem names or descriptors and cleans them through harness/process lifetime.

## Dependencies And Integration Points
Depends on the C library/shell runtime and local strace test harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/xgetdents.c -->
