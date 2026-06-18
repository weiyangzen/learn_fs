# sources/test-tools/ltp/testcases/kernel/syscalls/setsid/setsid01.c

## Purpose
Test to check the error and trivial conditions in setsid system call USAGE setsid01 RESTRICTIONS
This test doesn't follow good LTP format - PLEASE FIX!

## Important APIs, types, and functions
Important interfaces include syscall/library calls `setsid`, `setpgid`, `wait`, `kill`;
constants/macros `SIGKILL`; harness APIs `tst_parse_opts`, `tst_count`, `tst_fork`, `tst_resm`,
`tst_exit`, `tst_brkm`, `tst_sig`.

## Control flow
The legacy LTP `main()` parses standard options, calls `setup()`, loops with `TEST_LOOPING()`, runs
the syscall scenario, then calls `cleanup()` and `tst_exit()`. Helper functions include
`do_child_1`, `do_child_2`, `setup`, `cleanup`.

## State and persistence behavior
The test uses child processes and wait/exit status as observable state. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include legacy LTP `test.h` harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: signal and timeout based assertions depend on scheduler timing.

## Test signals
LTP result macros `TPASS`, `TFAIL`; expected errno/status values `EPERM`.
