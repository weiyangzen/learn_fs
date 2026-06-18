# sources/test-tools/ltp/testcases/kernel/syscalls/sgetmask/sgetmask01.c

## Purpose
NOTE: This case test the behavior of sgetmask # Sometime the returned "Oops"in this case don't mean
anything for # correct or error, we check the result between different kernel and # try to find if
there exist different returned code in different kernel #.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `sgetmask`, `ssetmask`; constants/macros
`SIGRTMAX`; harness APIs `tst_exit`, `tst_rmdir`, `tst_tmpdir`, `tst_parse_opts`, `tst_count`,
`TEST`, `tst_syscall`, `tst_resm`.

## Control flow
The legacy LTP `main()` parses standard options, calls `setup()`, loops with `TEST_LOOPING()`, runs
the syscall scenario, then calls `cleanup()` and `tst_exit()`. Helper functions include `cleanup`,
`setup`.

## State and persistence behavior
The test does not persist data beyond normal LTP build/runtime artifacts. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include legacy LTP `test.h` harness, temporary directory support, `lapi/syscalls.h`
compatibility wrappers. The file is built by the syscall directory Makefile and executed as part of
the LTP kernel syscall suite.

## Risks and edge cases
Key risks: obsolete or direct syscall paths may be absent or emulated differently on newer
architectures.

## Test signals
LTP result macros `TPASS`, `TINFO`.
