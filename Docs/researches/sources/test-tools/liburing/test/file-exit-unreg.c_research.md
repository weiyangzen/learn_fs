<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/file-exit-unreg.c -->
## sources/test-tools/liburing/test/file-exit-unreg.c

Purpose: checks that exiting a defer-taskrun ring with tagged registered files does not hit file unregistration/task-work locking bugs.

Important APIs/types/functions: `io_uring_queue_init` with `IORING_SETUP_SINGLE_ISSUER | IORING_SETUP_DEFER_TASKRUN`, `io_uring_register_files_tags`, `pipe`, and `io_uring_queue_exit`.

Control flow: the test creates a pipe, initializes a defer-taskrun single-issuer ring, registers both pipe fds with two tags, exits the ring, sleeps briefly, and returns success. Unsupported ring flags or tagged registration return skip.

State and persistence behavior: registered files carry tags, and unregistration occurs implicitly during `io_uring_queue_exit`.

Dependencies and integration points: integrates tagged fixed-file registration with deferred task-work cleanup.

Risks: no explicit CQE workload is submitted; this is a lockdep/lifetime sentinel rather than functional IO validation. Pipe fds are not explicitly closed.

Test signals: pass is no failure, hang, or lockdep-visible issue during ring exit after tagged file registration.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/file-exit-unreg.c -->
