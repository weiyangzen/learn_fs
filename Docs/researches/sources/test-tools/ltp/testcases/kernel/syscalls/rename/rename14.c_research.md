# sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename14.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename14.c` is a 166-line LTP source file in the `rename` syscall test area. rename filesystem semantics coverage for success, replacement, directory constraints, sticky permissions, hard links, and errno cases.

## Important APIs, Types, and Functions

called APIs/macros: `rename`; local functions: `term`, `al`, `dochild1`, `dochild2`, `main`; struct/table types referenced: `struct sigaction`; important macros/constants: `FAILED`, `PASSED`, `RUNTIME`.

## Control Flow

Function-level flow is organized around `term`, `al`, `dochild1`, `dochild2`, `main`. This file uses the older `test.h` harness: `main` parses options, loops over configured cases or signals, calls direct syscall wrappers, reports through `tst_resm`/`tst_brkm`, and exits through `tst_exit`. Some flow is concurrent: child processes or pthreads are used to exercise server, signal-delivery, or permission behavior, with waits/checkpoints joining the result. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem structure: files, directories, links, permissions, mount points, and expected post-rename path existence/content. Most cases mutate dentries and then validate the resulting tree.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `<errno.h>`, `<signal.h>`, `<stdlib.h>`, `<unistd.h>`, `<sys/wait.h>`, `<sys/types.h>`, `<sys/stat.h>`, `<fcntl.h>`, `"test.h"`. Uses the older LTP `test.h` harness and legacy result macros.

## Risks and Edge Cases

signal or child-process synchronization must avoid races

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TBROK for fixture/setup failures; notable reported messages include `rename14`; `./rename14`; `./rename14xyz`; `Test Passed`; `Test Failed`.
