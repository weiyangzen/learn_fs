<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/inotify.c -->
# sources/test-tools/strace/tests/inotify.c

## Purpose
Covers strace decoder coverage for `inotify_add_watch`. Source comments describe: Check decoding of inotify_add_watch and inotify_rm_watch syscalls. Source read: 71 lines, 2041 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <string.h>, <unistd.h>; defines: none; C functions: main; syscall names/numbers: inotify_add_watch, inotify_rm_watch, __NR_inotify_add_watch, __NR_inotify_rm_watch.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is inotify_add_watch, inotify_rm_watch, __NR_inotify_add_watch, __NR_inotify_rm_watch.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/inotify.c -->
