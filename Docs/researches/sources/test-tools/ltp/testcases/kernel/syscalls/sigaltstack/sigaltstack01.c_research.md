# sources/test-tools/ltp/testcases/kernel/syscalls/sigaltstack/sigaltstack01.c

## Purpose
Test Name: sigalstack01 Send a signal using the main stack. While executing the signal handler
compare a variable's address lying on the main stack with the stack boundaries returned by
sigaltstack(). Expected result: sigaltstack() should succeed to get/set signal alternate stack
context. Algorithm: Setup: Setup signal handling. Pause for SIGUSR1 if option specified. Test: Loop
if the proper options are given. Execute system call Check return code, if system call failed
(return=-1) Log the errno and Issue a FAIL message. Otherwise, Verify the Functionality of system
call if successful, Issue Functionality-Pass message. Otherwise, Issue Functionality-Fail message.
Cleanup: Print errno log.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `sigaction`, `sigaltstack`, `kill`; types `struct
sigaction`; constants/macros `SIGUSR1`, `SIGSTKSZ`, `SIGUSER1`; harness APIs `tst_parse_opts`,
`tst_count`, `TEST`, `tst_resm`, `tst_brkm`, `tst_exit`, `tst_sig`.

## Control flow
The legacy LTP `main()` parses standard options, calls `setup()`, loops with `TEST_LOOPING()`, runs
the syscall scenario, then calls `cleanup()` and `tst_exit()`. Helper functions include `setup`,
`cleanup`, `sig_handler`.

## State and persistence behavior
The test changes per-process signal dispositions, masks, pending queues, or alternate signal stack
state. State is scoped to the LTP process tree unless a privileged syscall changes host-visible
kernel state before cleanup.

## Dependencies and integration points
Dependencies include legacy LTP `test.h` harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
LTP result macros `TPASS`, `TFAIL`.
