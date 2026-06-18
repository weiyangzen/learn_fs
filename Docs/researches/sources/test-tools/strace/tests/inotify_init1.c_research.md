<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/inotify_init1.c -->
# sources/test-tools/strace/tests/inotify_init1.c

## Purpose
Covers strace decoder coverage for `inotify_init1`. Source comments describe: Check decoding of inotify_init1 syscall. IN_??? Kernels that do not have v2.6.33-rc1~34^2~7 do not have "anon_inode:" prefix. Let's assume that it can be either "inotify" or "anon_inode:inotify" for now, as any change there may be of interest. Source read: 107 lines, 2411 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>, "kernel_fcntl.h"; defines: all_flags, RC_FMT; C functions: main; syscall names/numbers: inotify_init1, __NR_inotify_init1.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is inotify_init1, __NR_inotify_init1.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, `/proc/self/fd`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling; path-decoding variants require procfs fd links. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/inotify_init1.c -->
