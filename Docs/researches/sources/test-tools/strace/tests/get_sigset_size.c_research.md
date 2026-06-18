<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/get_sigset_size.c -->
# sources/test-tools/strace/tests/get_sigset_size.c

## Purpose
Covers strace self-test coverage for `get_sigset_size`. Source comments describe: Find out the size of kernel's sigset_t. If the sigset size specified to rt_sigprocmask is not equal to the size of kernel's sigset_t, the kernel does not look at anything else and fails with EINVAL. Otherwise, if both pointers specified to rt_sigprocmask are NULL, the kernel just returns 0. This vaguely documented kernel feature can be used to probe the. Source read: 47 lines, 1089 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <signal.h>, <unistd.h>, "scno.h"; defines: none; C functions: get_sigset_size; syscall names/numbers: rt_sigprocmask, __NR_rt_sigprocmask.

## Control Flow
nested loops cover flag, pointer, size, fd, and translation-mode combinations. primary syscall coverage is rt_sigprocmask, __NR_rt_sigprocmask.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/get_sigset_size.c -->
