# sources/test-tools/ltp/testcases/kernel/syscalls/signal/signal06.c

## Purpose
save_xstate_sig()->drop_init_fpu() doesn't look right. setup_rt_frame() can fail after that, in this
case the next setup_rt_frame() triggered by SIGSEGV won't save fpu simply because the old state was
lost. This obviously mean that fpu won't be restored after sys_rt_sigreturn() from SIGSEGV handler.
These commits fix the issue on v3.17-rc3-3 stable kernel: commit
df24fb859a4e200d9324e2974229fbb7adf00aef Author: Oleg Nesterov <oleg@redhat.com> Date: Tue Sep 2
19:57:17 2014 +0200 commit 66463db4fc5605d51c7bb81d009d5bf30a783a2c Author: Oleg Nesterov
<oleg@redhat.com> Date: Tue Sep 2 19:57:13 2014 +0200 Reproduce: Test-case (needs -O2). Referenced
kernel commit ids include `df24fb859a4e200d9324e2974229fbb7adf00aef`,
`66463db4fc5605d51c7bb81d009d5bf30a783a2c`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `sigaction`, `sigaltstack`, `mprotect`,
`pthread_create`, `pthread_join`; types `struct sigaction`; constants/macros `SIGSEGV`, `SIGHUP`;
harness APIs `tst_resm`, `tst_exit`, `TEST`, `tst_brkm`, `tst_parse_opts`, `tst_count`.

## Control flow
The legacy LTP `main()` parses standard options, calls `setup()`, loops with `TEST_LOOPING()`, runs
the syscall scenario, then calls `cleanup()` and `tst_exit()`. Helper functions include `test`,
`sigh`.

## State and persistence behavior
The test changes per-process signal dispositions, masks, pending queues, or alternate signal stack
state; maps or protects temporary memory for buffers, alternate stacks, or coordination. State is
scoped to the LTP process tree unless a privileged syscall changes host-visible kernel state before
cleanup.

## Dependencies and integration points
Dependencies include legacy LTP `test.h` harness, `lapi/syscalls.h` compatibility wrappers. The file
is built by the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: obsolete or direct syscall paths may be absent or emulated differently on newer
architectures.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TBROK`, `TCONF`, `TINFO`, `TTERRNO`, `TERRNO`.
