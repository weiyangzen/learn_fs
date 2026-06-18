# sources/security-integrity/libcap/tests/psx_test.c

Purpose: C test for raw `psx_syscall()` synchronization across pthreads, forks, execs, and keepcaps transitions.

Important APIs/functions: `say_hello_expecting()` checks `PR_GET_KEEPCAPS`. Worker `say_hello()` waits on condition variables and validates shared keepcaps over several steps. Main toggles keepcaps with `psx_syscall(SYS_prctl, PR_SET_KEEPCAPS, ...)`, starts threads, forks/execs a child, and joins threads.

Control flow: ten iterations alternate keepcaps, notify all launched threads to validate state, add threads in early iterations, then join them in later iterations. A forked child execs the same binary with a stop argument.

State and dependencies: mutates keepcaps, uses pthread mutex/cond, fork/exec/wait, and libpsx public header.

Risks and test signals: catches missed threads, stale state after fork/exec, and synchronization deadlocks in the core C PSX path.
