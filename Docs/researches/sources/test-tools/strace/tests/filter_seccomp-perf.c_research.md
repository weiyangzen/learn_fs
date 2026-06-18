<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/filter_seccomp-perf.c -->
# sources/test-tools/strace/tests/filter_seccomp-perf.c

## Purpose
Covers seccomp filter performance. Source comments describe: Check seccomp filter performance. Source read: 39 lines, 589 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <signal.h>, <stdbool.h>, <stdio.h>, <unistd.h>; defines: none; C functions: handler, main.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. nested loops cover flag, pointer, size, fd, and translation-mode combinations.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: seccomp-BPF availability and filter installation can vary by kernel/configuration; timing/performance checks need tolerance for scheduler noise. Test signals: program stdout contains the canonical expected strace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/filter_seccomp-perf.c -->
