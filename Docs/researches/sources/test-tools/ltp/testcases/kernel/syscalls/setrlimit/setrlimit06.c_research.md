# sources/test-tools/ltp/testcases/kernel/syscalls/setrlimit/setrlimit06.c

## Purpose
Set CPU time limit for a process and check its behavior after reaching CPU time limit - Process got
SIGXCPU after reaching soft limit of CPU time - Process got SIGKILL after reaching hard limit of CPU
time Test is also a regression test for kernel bug from v4.17: c3bca5d450b62 ("posix-cpu-timers:
Ensure set_process_cpu_timer is always evaluated"). Referenced kernel commit ids include
`c3bca5d450b62`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `setrlimit`, `setrlimit_u64`, `alarm`; types
`struct rlimit`, `struct rlimit64`, `struct tst_test`, `struct tst_buffers`, `struct tst_tag`;
constants/macros `SIGXCPU`, `SIGKILL`, `RLIMIT_CPU`, `SIGALRM`; safe wrappers `SAFE_SIGNAL`,
`SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_FORK`, `SAFE_WAITPID`; harness APIs `tst_test`, `tst_variant`,
`TEST`, `tst_res`, `tst_strstatus`, `tst_buffers`, `tst_tag`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test_all`, `.test`, `.test_variants`, `.forks_child`. Local functions include `sighandler`,
`setup`, `cleanup`, `verify_setrlimit`.

## State and persistence behavior
The test uses child processes and wait/exit status as observable state; maps or protects temporary
memory for buffers, alternate stacks, or coordination; changes resource limits in the current
process or child process. State is scoped to the LTP process tree unless a privileged syscall
changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, LTP syscall ABI variants. The file is built by
the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: signal and timeout based assertions depend on scheduler timing.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TTERRNO`, `TERRNO`.
