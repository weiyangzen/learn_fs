<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex2test.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex2test.h

Purpose: Header helper for futex2/futex_waitv tests, wrapping `__NR_futex_waitv` and time64 ABI differences. Source notes: Futex2 library addons for futex tests futex_waitv - Wait at multiple futexes, wake on any @waiters: Array of waiters @nr_waiters: Length of waiters array @flags: Operation flags @timo: Optional timeout for operation _FUTEX2TEST_H The file was read in full for this report (47 lines, 1140 bytes).

Important APIs/types/functions: types/structs: struct timespec64, struct futex_waitv, struct timespec; functions: futex_waitv; local macros/constants: FUTEX2TEST_H.

Control flow: the file provides declarations/helpers consumed by sibling tests.

State and persistence behavior: The test manipulates futex words and scheduler-visible wait queues. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `stdint.h`, `lapi/syscalls.h`, `futextest.h`, `lapi/abisize.h`; integrates with the LTP futex syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: key constants: __NR_futex_waitv.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex2test.h -->
