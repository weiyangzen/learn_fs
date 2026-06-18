# sources/test-tools/ltp/testcases/kernel/syscalls/sched_getattr/sched_getattr01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/sched_getattr/sched_getattr01.c` is a 105-line LTP source file in the `sched_getattr` syscall test area. sched_getattr scheduler attribute readback coverage after setting SCHED_DEADLINE parameters.

## Important APIs, Types, and Functions

called APIs/macros: `sched_getattr`, `sched_setattr`; local functions: `main`; struct/table types referenced: `struct sched_attr`; important macros/constants: `_GNU_SOURCE`, `RUNTIME_VAL`, `PERIOD_VAL`, `DEADLINE_VAL`.

## Control Flow

Function-level flow is organized around `main`. This file uses the older `test.h` harness: `main` parses options, loops over configured cases or signals, calls direct syscall wrappers, reports through `tst_resm`/`tst_brkm`, and exits through `tst_exit`. Some flow is concurrent: child processes or pthreads are used to exercise server, signal-delivery, or permission behavior, with waits/checkpoints joining the result. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is scheduler state for the current process/thread: the test sets a SCHED_DEADLINE policy and reads back a `struct sched_attr` to compare runtime, period, and deadline fields. The test expects root privileges or temporarily changes credentials/capabilities.

## Dependencies and Integration Points

Direct includes: `<unistd.h>`, `<stdio.h>`, `<stdlib.h>`, `<string.h>`, `<time.h>`, `<linux/unistd.h>`, `<linux/kernel.h>`, `<linux/types.h>`, `<sys/syscall.h>`, `<pthread.h>`, `<errno.h>`, `"test.h"`, `"lapi/sched.h"`. Uses the older LTP `test.h` harness and legacy result macros. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

Scheduler deadline tests require privileges and kernel SCHED_DEADLINE support; systems without the policy or with constrained runtime/deadline settings should fail setup rather than misreporting readback behavior.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `lapi/sched.h`; `sched_getattr01`; `sched_setattr() failed`; `sched_getattr() failed`; `sched_runtime is incorrect (%`.
