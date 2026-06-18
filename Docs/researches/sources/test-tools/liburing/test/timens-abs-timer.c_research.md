# sources/test-tools/liburing/test/timens-abs-timer.c

Purpose: regression test that absolute io_uring timers honor the caller's time namespace. It targets `IORING_TIMEOUT_ABS` and `IORING_ENTER_ABS_TIMER`, both of which must convert namespace-visible absolute monotonic deadlines to host time instead of firing immediately under a shifted time namespace.

Important APIs/types/functions: `write_one`, `enter_unpriv_userns_timens`, `ts_to_ns`, `elapsed_ns`, `test_op_timeout_abs`, `test_enter_abs_timer`, `run_tests_in_timens_grandchild`, `run_in_timens`, `unshare(CLONE_NEWUSER | CLONE_NEWTIME)`, `/proc/self/{setgroups,uid_map,gid_map,timens_offsets}`, `io_uring_prep_timeout`, and `io_uring_enter2`.

Control flow: main forks so namespace setup cannot contaminate the parent. The child creates a user and time namespace, maps uid/gid 0, applies a `monotonic -10 0` offset, then forks a grandchild because time namespaces apply to future children. The grandchild runs both timer paths with an absolute deadline of current monotonic time plus one second and validates observed elapsed time.

State/persistence behavior: no filesystem state beyond procfs namespace control writes. The durable state under test is kernel timer conversion state associated with the task namespace and io_uring wait/timeout paths.

Dependencies/integration: requires kernel time namespace support, permission to create unprivileged user namespaces, `IORING_FEAT` support sufficient for the tested operations, and direct syscall wrappers from `../src/syscall.h`.

Risks/test signals: skips for unsupported or prohibited namespaces. A failure is an elapsed time under 100 ms, strongly indicating missing `timens_ktime_to_host()` conversion; under 900 ms is also treated as early firing.
