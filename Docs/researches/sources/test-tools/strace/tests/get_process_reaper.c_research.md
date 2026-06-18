<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/get_process_reaper.c -->
# sources/test-tools/strace/tests/get_process_reaper.c

## Purpose
Covers strace self-test coverage for `get_process_reaper`. Source comments describe: Print the process reaper id. PARENT - CHILD - GRANDCHILD wait for notification from PARENT about CHILD completion write ppid to PARENT wait for CHILD completion notify GRANDCHILD about CHILD completion read ppid of GRANDCHILD CHILD PARENT Source read: 108 lines, 2180 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>, <unistd.h>, <sys/wait.h>; defines: parent_read_fd, grandchild_write_fd, grandchild_read_fd, parent_write_fd; C functions: grandchild, child, parent, main.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. process/thread branches use `fork`, `pthread`, pipes, or wait helpers to produce traceable lifecycle events.

## State And Persistence Behavior
child processes or threads are synchronized and reaped before test exit.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: concurrency and process ordering can make trace matching fragile. Test signals: program stdout contains the canonical expected strace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/get_process_reaper.c -->
