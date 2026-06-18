# sources/test-tools/liburing/test/sqpoll-exit-hang.c

Purpose: tests that process exit with SQPOLL and a request polling the ring fd itself does not hang due to circular references.

Important APIs/types/functions: `IORING_SETUP_SQPOLL`, `IORING_FEAT_SQPOLL_NONFIXED`, `io_uring_prep_poll_add`, ring fd polling, and `mtime_since_now`.

Control flow: creates an SQPOLL ring with short idle timeout, skips if setup unsupported or lacks nonfixed SQPOLL, queues a poll on `ring.ring_fd`, submits it, sleeps for about one second, and returns without explicit ring teardown.

State/persistence behavior: kernel ring fd and pending poll request form the reference cycle under test. No filesystem state.

Dependencies/integration: may require root for SQPOLL on older kernels. Feature absence leads to skip-style success.

Risks/test signals: a bad kernel may hang on process exit or ring teardown. The program has minimal runtime assertions because liveness at exit is the signal.
