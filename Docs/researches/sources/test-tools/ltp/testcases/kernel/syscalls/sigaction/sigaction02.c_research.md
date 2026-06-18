# sources/test-tools/ltp/testcases/kernel/syscalls/sigaction/sigaction02.c

## Purpose
Testcase to check the basic errnos set by the sigaction(2) syscall. ALGORITHM 1. Pass an invalid
signal as the "sig" parameter, and expect EINVAL. 2. Attempt to catch the SIGKILL, and expect
EINVAL. 3. Attempt to catch the SIGSTOP, and expect EINVAL. 4. Pass an invalid address as the "act"
parameter, expect an EFAULT. 5. Pass an invalid address as the "oact" parameter, and expect EFAULT.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `sigaction`, `sigemptyset`, `sigaddset`; types
`struct sigaction`; constants/macros `SIGKILL`, `SIGSTOP`, `SIGBAD`, `SIGUSR1`; harness APIs
`tst_resm`, `tst_parse_opts`, `tst_exit`.

## Control flow
The legacy LTP `main()` parses standard options, calls `setup()`, loops with `TEST_LOOPING()`, runs
the syscall scenario, then calls `cleanup()` and `tst_exit()`. Helper functions include `setup`,
`cleanup`, `handler`, `set_handler`.

## State and persistence behavior
The test changes per-process signal dispositions, masks, pending queues, or alternate signal stack
state. State is scoped to the LTP process tree unless a privileged syscall changes host-visible
kernel state before cleanup.

## Dependencies and integration points
Dependencies include legacy LTP `test.h` harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: signal and timeout based assertions depend on scheduler timing; invalid-address tests can
expose architecture-specific fault delivery.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TINFO`; expected errno/status values `EINVAL`, `EFAULT`.
