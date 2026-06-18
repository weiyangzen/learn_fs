<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/test_ucopy.c -->
# sources/test-tools/strace/tests/test_ucopy.c

## Purpose
Covers strace decoder coverage for `test_ucopy`. Source comments/macros state: Test whether process_vm_readv and PTRACE_PEEKDATA work. !HAVE_PROCESS_VM_READV Source read: 142 lines, 2716 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <errno.h>, <sys/ptrace.h>, <signal.h>, <stdlib.h>, <unistd.h>, <sys/uio.h>, <sys/wait.h>, "test_ucopy.h", "scno.h"; defines/undefs: process_vm_readv; C functions: call_process_vm_readv, call_ptrace_peekdata, test_ucopy, test_process_vm_readv, test_ptrace_peekdata; syscall numbers/wrappers: process_vm_readv, __NR_process_vm_readv; struct types: iovec.

## Control Flow
loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations. process/thread branches synchronize children or threads before final trace comparison. primary syscall coverage: process_vm_readv, __NR_process_vm_readv.

## State And Persistence Behavior
owns transient child/thread lifecycle state that must be synchronized before exit.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `test_ucopy.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; process/thread ordering can make trace matching fragile. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/test_ucopy.c -->
