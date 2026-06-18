<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/files-exit-hang-poll.c -->
## sources/test-tools/liburing/test/files-exit-hang-poll.c

Purpose: regression test for process/ring exit hangs when a request pins the task file table and is linked to an unfinished poll.

Important APIs/types/functions: `add_poll`, `add_accept`, `setup_io_uring`, `t_bind_ephemeral_port`, `io_uring_prep_poll_add`, `io_uring_prep_accept`, `IOSQE_IO_LINK`, and `alarm`.

Control flow: the test creates a nonblocking TCP listener on an ephemeral port, initializes a ring, queues a linked poll on the listening socket followed by an accept, submits both, installs a one-second alarm that exits successfully, and waits for a CQE that should normally not arrive.

State and persistence behavior: global `ring` and listening socket remain live while the alarm triggers process exit. The intentional behavior is abrupt exit with pending linked requests.

Dependencies and integration points: integrates socket listen state, poll, accept, linked SQEs, and task file table cleanup.

Risks: the alarm-based success path means a hang is detected by external test timeout rather than explicit code. If a CQE arrives unexpectedly, the ring exits and returns pass.

Test signals: pass means the process exits rather than hanging with linked poll/accept file-table references.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/files-exit-hang-poll.c -->
