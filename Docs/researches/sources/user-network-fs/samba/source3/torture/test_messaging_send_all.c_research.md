# sources/user-network-fs/samba/source3/torture/test_messaging_send_all.c

Purpose: This file tests `messaging_send_all()` broadcast behavior. It verifies that all forked responder processes receive a broadcast ping and reply with pongs, while the sender does not receive its own broadcast.

Important APIs/types/functions: `fork_responder()` forks a child using a shared messaging context, calls `messaging_reinit()` in the child, signals readiness, and waits on an exit pipe. `collect_pong_send()` creates a request that repeatedly calls `messaging_read_send()` for `MSG_PONG`. `collect_pong_received()` tracks which child pids have replied and rejects a pong from the parent pid. The public entrypoint is `run_messaging_send_all()`.

Control flow: The parent initializes tevent and messaging, creates an exit pipe, forks `MAX(5, torture_nprocs)` responders, starts pong collection with a ten-second endtime, calls `messaging_send_all(MSG_PING)`, polls until all children have replied, closes the exit pipe, and waits for every child.

State/persistence behavior: State is transient process and messaging state: child pid array, exit/ready pipes, tevent request state, and the list of senders still expected. No files or databases are written. Children exit when the parent closes the exit pipe they are watching.

Dependencies and integration points: It depends on Samba messaging broadcast semantics, `messaging_reinit()` after fork, `wait_for_read_send()` from async socket helpers, sys read/write wrappers, and global `torture_nprocs`. It validates broadcast messaging used for daemon notifications.

Risks: Broadcast fan-out is sensitive to process registration timing, so `fork_responder()` blocks until each child signals readiness. The test rejects self-broadcasts with `EMULTIHOP`; any semantic change that includes the sender will fail. High `torture_nprocs` increases process and message load.

Test signals: Passing requires all expected child pids to produce one `MSG_PONG`, no pong from the parent pid, successful collection before the ten-second endtime, and successful `waitpid()` for every responder.
