<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl33.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl33.c

Purpose: Fork/checkpoint lease-breaking test covering write/read leases against conflicting open/truncate operations and `/proc/sys/fs/lease-break-time` restoration. Source notes: Author: Guangwen Feng <fenggw-fnst@cn.fujitsu.com> DESCRIPTION Test for feature F_SETLEASE of fcntl(2). "F_SETLEASE is used to establish a lease which provides a mechanism: When a process (the lease breaker) performs an open(2) or truncate(2) that conflicts with the lease, the system call will be blocked by kernel, meanwhile the kernel notifies the lease holder by sending it a signal (SIGIO by default), after the lease holder successes to downgrade or remove the lease, the kernel permits the system call of the lease breaker to proceed." MIN_TIME_LIMIT is defined to 5 senconds as a minimal acceptable amount of time for the lease breaker waiting for unblock via lease holder voluntarily downgrade or remove the lease, if the lease breaker is unblocked within MIN_TIME_LIMIT we may consider that the feature of the lease mechanism works well.... The file was read in full for this report (229 lines, 5579 bytes).

Important APIs/types/functions: calls/wrappers: fcntl(), open(), truncate(), SAFE_FILE_SCANF, SAFE_FILE_PRINTF, SAFE_TOUCH, SAFE_FORK, SAFE_OPEN, TST_CHECKPOINT_WAKE, SAFE_CLOSE, TST_CHECKPOINT_WAIT, SAFE_TRUNCATE; types/structs: struct timespec, struct test_case_t, struct tst_test; functions: setup, do_test, do_child, cleanup; local macros/constants: MIN_TIME_LIMIT, OP_OPEN_RDONLY, OP_OPEN_WRONLY, OP_OPEN_RDWR, OP_TRUNCATE, FILE_MODE, PATH_LS_BRK_T.

Control flow: setup path: setup; exercise path: do_test, do_child; cleanup path: cleanup; notable execution mechanics: iterates a case table, forks child processes for concurrency or privilege separation, uses LTP checkpoints to order parent/child actions.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, child processes and wait status, kernel tunables that setup/cleanup must restore, UID/capability-sensitive kernel state, temporary mount/test filesystem state, advisory locks or file leases. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `tst_test.h`, `tst_timer.h`, `tst_safe_macros.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros.

Risks: requires root/capability-sensitive behavior; filesystem-specific semantics can change expected results; must restore proc/sys tunables after failures; scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EAGAIN; key constants: F_SETLEASE, SIGIO, PATH_LS_BRK_T, F_WRLCK, O_RDONLY, O_WRONLY, O_RDWR, F_RDLCK, CLOCK_MONOTONIC, F_UNLCK; harness metadata: .forks_child, .needs_root, .needs_checkpoints, .tcnt, .setup, .test, .cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl33.c -->
