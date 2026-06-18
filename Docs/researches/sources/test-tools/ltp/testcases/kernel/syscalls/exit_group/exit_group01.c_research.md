# sources/test-tools/ltp/testcases/kernel/syscalls/exit_group/exit_group01.c

Purpose: Checks that raw `exit_group()` terminates a child process and all its running threads with the requested status.

Important APIs/types/functions: `pthread_create` through `SAFE_PTHREAD_CREATE`, `tst_syscall(__NR_exit_group, 4)`, shared anonymous `mmap`, `tst_atomic_t`, `tst_gettid`, `sched_yield`, and `SAFE_WAITPID`.

Control flow: `setup()` allocates shared `worker_data` for at least two CPUs. The child starts one busy worker per CPU and calls `exit_group(4)`. The parent waits for exit status 4 and then snapshots counters to verify they no longer change.

State and persistence behavior: Shared mmap state records worker tids and counters across fork. After `exit_group`, counters should remain stable because all child threads are gone.

Dependencies and integration points: Requires pthread linking, fork support, and anonymous shared mapping; `.needs_checkpoints` is declared although no explicit checkpoint macro is used.

Risks and test signals: If any worker survives the group exit, counters continue changing and the test fails. A failed syscall or wrong wait status also fails.
