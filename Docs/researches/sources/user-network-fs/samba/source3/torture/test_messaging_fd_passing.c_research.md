# sources/user-network-fs/samba/source3/torture/test_messaging_fd_passing.c

Purpose: This file tests Unix file-descriptor passing through Samba's messaging layer. It covers self-send behavior and parent-to-child fd passing with large, small, and zero payloads to exercise both queued/fragmented and fast paths.

Important APIs/types/functions: `run_messaging_fdpass1()` sends one pipe fd to its own `messaging_server_id()`. `fdpass2_filter()` selects messages with `MSG_TORTURE_FDPASS2` and exactly two fds. `fdpass2_child()` waits with `messaging_filtered_read_send()/recv()` and echoes a byte between passed pipes. `fdpass2_parent()` creates up/down pipes, sends fds with `messaging_send_iov()`, waits for child readiness through tevent fd callbacks, and verifies byte round-trip. Public variants are `run_messaging_fdpass2()`, `run_messaging_fdpass2a()`, and `run_messaging_fdpass2b()`.

Control flow: The parent and child synchronize on a ready pipe. The parent sends the child's process id as the message destination, passes the read end of one pipe and write end of another, closes its copies after child confirmation, writes a byte, and expects to read the same byte back. Payload size is parameterized: 1 MB for fragmentation/reassembly, one byte for fast path with payload, and zero bytes for fast path without payload.

State/persistence behavior: State is transient IPC: pipes, process ids, messaging sockets, tevent fd handlers, and talloc frames. No durable data is written. Correctness depends on fd lifetime and close ordering after descriptor transfer.

Dependencies and integration points: It depends on Samba messaging, tevent Unix helpers, fork/wait, DATA_BLOB/iovec payload handling, and messaging fd-passing support. It validates infrastructure used by source3 daemons to transfer descriptors between processes.

Risks: Platform support for Unix-domain fd passing is required. The large payload path can expose resource limits or socket buffering issues. Child readiness and completion use byte pipes, so missed synchronization can deadlock or fail the test.

Test signals: Passing requires `messaging_send_iov()` OK, filtered read receiving exactly two fds, child confirmation, successful byte round-trip through passed descriptors, and child `waitpid()` success for all three payload variants.
