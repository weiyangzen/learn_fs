# sources/test-tools/liburing/test/tty-write-dpoll.c

Purpose: regression test for double-poll TTY write behavior, targeting a kernel bug where io_uring assumed the triggered poll waitqueue was the only poll.

Important APIs/types/functions: `open("/dev/ttyS0", O_RDWR | O_NONBLOCK)`, `t_create_ring`, `io_uring_get_sqe`, `io_uring_prep_writev`, `io_uring_submit`, `struct iovec`, `SQES`, and `BUFSIZE`.

Control flow: main skips when invoked with arguments or when `/dev/ttyS0` is absent. It creates a 128-entry ring, queues 128 nonblocking `writev` operations to the TTY using identical static buffer storage, and submits them all. It only verifies the submit count.

State/persistence behavior: no durable state. It writes to a serial TTY if present, so runtime device output is possible.

Dependencies/integration: depends on a real `/dev/ttyS0`, nonblocking TTY driver write/poll behavior, and liburing test helpers.

Risks/test signals: intentionally opportunistic and returns success when no TTY exists. Failure is a ring setup error or submission count mismatch; completions are not reaped, so this is mainly a regression trigger for kernel-side poll handling.
