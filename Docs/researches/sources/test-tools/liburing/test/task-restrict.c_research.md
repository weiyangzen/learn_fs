# sources/test-tools/liburing/test/task-restrict.c

Purpose: tests per-task io_uring restrictions registered with fd `-1`, including SQE opcode restrictions, fork inheritance, double-registration rejection, and register-op restrictions.

Important APIs/types/functions: raw `__sys_io_uring_register(-1, IORING_REGISTER_RESTRICTIONS, ...)`, `struct io_uring_restriction`, `IORING_RESTRICTION_SQE_OP`, `IORING_RESTRICTION_REGISTER_OP`, `PR_SET_NO_NEW_PRIVS`, fork/wait, and expected `-EACCES`/`-EPERM`.

Control flow: each test runs in a child because restrictions cannot be removed. `test_task_restrict_sqe_op()` allows only NOP and verifies READ is denied. `test_task_restrict_fork_inherit()` registers NOP/WRITE allowance, forks a grandchild, and verifies READ denial there. `test_task_restrict_double_register()` expects a second registration to fail with `-EPERM`. `test_task_restrict_register_op()` allows file registration and verifies buffer registration is denied.

State/persistence behavior: restrictions are per-task kernel state inherited through fork. No persistent files are created.

Dependencies/integration: requires per-task restriction support and `no_new_privs`, similar to seccomp-style constraints. Unsupported `-EINVAL`/`-EBADF` skips.

Risks/test signals: catches missing inheritance, over-permissive SQE/register operations, incorrect double-registration errno, or failure to apply restrictions to newly created rings.
