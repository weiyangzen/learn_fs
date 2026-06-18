<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/syscall.c -->
## sources/test-tools/liburing/src/syscall.c

Purpose: exposes public syscall wrapper symbols for `io_uring_enter`, `io_uring_enter2`, `io_uring_setup`, and `io_uring_register`.

Important APIs/types/functions: each wrapper delegates to the corresponding internal `__sys_io_uring_*` helper declared in `syscall.h`. `io_uring_enter` takes a signal mask pointer; `io_uring_enter2` takes the extended argument pointer and size.

Control flow: one syscall wrapper call per function, returning the internal helper result, which is normalized to negative errno on failure.

State and persistence behavior: no local state. Kernel ring state is changed by the syscalls.

Dependencies and integration points: uses `liburing.h`, `syscall.h`, and `io_uring.h`. Public applications may call these lower-level wrappers directly, while higher-level setup/queue/register code uses internal wrappers.

Risks: public wrappers must preserve liburing's convention of returning negative errno rather than setting `errno` only. Signature drift would break ABI consumers.

Test signals: low-level tests and direct syscall-path tests validate these wrappers; most suite tests use higher-level APIs that transitively use the same syscall layer.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/syscall.c -->
