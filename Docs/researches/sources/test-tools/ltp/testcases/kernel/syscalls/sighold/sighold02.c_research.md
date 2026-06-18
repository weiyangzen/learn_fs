# sources/test-tools/ltp/testcases/kernel/syscalls/sighold/sighold02.c

## Purpose
This test checks following conditions: 1. sighold action to turn off the receipt of all signals was
done without error. 2. After signals were held, and sent, no signals were trapped.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `sighold`; types `struct tst_test`;
constants/macros `SIGRTMIN`, `SIGCHLD`, `SIGKILL`, `SIGALRM`, `SIGSTOP`; safe wrappers
`SAFE_SIGNAL`, `SAFE_FORK`, `SAFE_KILL`; harness APIs `tst_test`, `tst_brk`, `tst_strsig`,
`tst_res`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.test_all`, `.test`,
`.forks_child`. Local functions include `skip_sig`, `handle_sigs`, `do_child`, `run`.

## State and persistence behavior
The test uses child processes and wait/exit status as observable state; changes per-process signal
dispositions, masks, pending queues, or alternate signal stack state. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: signal and timeout based assertions depend on scheduler timing.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TBROK`, `TINFO`, `TERRNO`.
