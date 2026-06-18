<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/int_flags.h -->
## sources/test-tools/liburing/src/int_flags.h

Purpose: defines liburing-private internal flag bits stored in `struct io_uring::int_flags` and computes enter flags for registered-ring and iowait behavior.

Important APIs/types/functions: `INT_FLAGS_MASK` covers `IORING_ENTER_REGISTERED_RING` and `IORING_ENTER_NO_IOWAIT`. Internal bits are `INT_FLAG_REG_RING`, `INT_FLAG_APP_MEM`, `INT_FLAG_REG_REG_RING`, `INT_FLAG_CQ_ENTER`, and `INT_FLAG_NO_IOWAIT`. `ring_enter_flags()` masks `int_flags` down to syscall-visible enter flags.

Control flow: setup/registration code mutates `int_flags`; queue submission and wait code calls `ring_enter_flags()` before `io_uring_enter`.

State and persistence behavior: `int_flags` records runtime state such as whether the ring fd is registered, whether app memory backs a no-mmap ring, whether CQ enter is required, and whether to suppress iowait.

Dependencies and integration points: included by `queue.c`, `setup.c`, and `register.c`, and depends on public enter flag constants from `io_uring.h`.

Risks: internal bits share an 8-bit field and must not collide with syscall-visible flag bits used by `INT_FLAGS_MASK`. Incorrect flags can send io_uring_enter to the wrong fd mode or leak/unmap app memory incorrectly.

Test signals: registered ring-fd tests, no-mmap setup tests, IOPOLL/SQPOLL behavior, and iowait feature tests validate this indirectly.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/int_flags.h -->
