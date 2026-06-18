<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fsync-y.c -->
# sources/test-tools/strace/tests/fsync-y.c

## Purpose
Covers printing of file name in strace -y mode. Source comments describe: Check printing of file name in strace -y mode. Source read: 53 lines, 1149 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <fcntl.h>, <limits.h>, <stdio.h>, <unistd.h>; defines: none; C functions: main.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. nested loops cover flag, pointer, size, fd, and translation-mode combinations.

## State And Persistence Behavior
opens descriptors, commonly `/dev/null`, `/dev/full`, or the current directory, for fd/path decoding.

## Dependencies And Integration Points
Depends on `tests.h`, `/proc/self/fd`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: path-decoding variants require procfs fd links. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fsync-y.c -->
