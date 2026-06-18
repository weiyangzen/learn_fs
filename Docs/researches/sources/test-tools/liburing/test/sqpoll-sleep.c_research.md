# sources/test-tools/liburing/test/sqpoll-sleep.c

Purpose: verifies an SQPOLL thread goes idle around the configured timeout and sets `IORING_SQ_NEED_WAKEUP`.

Important APIs/types/functions: `IORING_SETUP_SQPOLL`, `sq_thread_idle`, `IORING_SQ_NEED_WAKEUP`, `IO_URING_READ_ONCE`, `io_uring_prep_nop`, and `mtime_since_now`.

Control flow: creates an SQPOLL ring with idle 100 ms, submits and reaps a NOP, then polls `*ring.sq.kflags` until `IORING_SQ_NEED_WAKEUP` appears or one second elapses. It requires wakeup timing between roughly 90 and 110 ms.

State/persistence behavior: state is SQPOLL kthread idle/wakeup flag. No external state.

Dependencies/integration: SQPOLL setup may require privileges; unsupported setup skips. Timing depends on scheduler behavior.

Risks/test signals: catches missing wakeup flag or significantly wrong idle timing, but may be sensitive to overloaded systems.
