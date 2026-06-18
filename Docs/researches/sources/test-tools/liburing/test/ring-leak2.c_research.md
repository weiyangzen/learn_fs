# sources/test-tools/liburing/test/ring-leak2.c

Purpose: reproduces a two-ring deadlock/leak pattern where server and client rings hold pending poll/eventfd operations and a circular reference can prevent full exit.

Important APIs/types/functions: `io_uring_queue_init_params`, raw `__sys_io_uring_enter`, `io_uring_prep_poll_add`, `io_uring_prep_read`, `IOSQE_ASYNC`, `eventfd`, pthreads, nonblocking TCP listener sockets, and packed `conn_info` stored in `sqe->user_data`.

Control flow: a server thread creates a nonblocking TCP listener and eventfd, queues eventfd read and listener poll, and on completions may submit the client ring under a mutex. A client thread creates its own ring, queues an async eventfd read, enters the ring manually with `IORING_ENTER_GETEVENTS`, and requeues eventfd reads. `main()` starts both threads and exits via a one-second `SIGALRM`.

State/persistence behavior: all state is process-local sockets, eventfds, ring CQ/SQ state, and cross-thread pointer state (`client_ring`, `client_eventfd`). No filesystem persistence is used.

Dependencies/integration: exercises io_uring poll/read on eventfds and sockets, raw enter behavior, pthread synchronization, and teardown of rings with pending operations. The alarm bounds the regression.

Risks/test signals: the intended failure is a hang or unkillable pending io-wq/ring reference cycle. Because success is time-bounded exit, this is a liveness regression test with limited semantic assertions.
