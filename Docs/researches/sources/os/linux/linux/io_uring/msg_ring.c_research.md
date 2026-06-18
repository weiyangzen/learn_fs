# File Research: sources/os/linux/linux/io_uring/msg_ring.c

Implements `IORING_OP_MSG_RING` and synchronous message-ring delivery.

Key flows:
- Prep parses destination user data, length, command, source fd, destination fixed slot/CQE flags, and validates `IORING_MSG_RING_*` flags.
- Data messages post auxiliary CQEs to the target ring; task-complete target rings receive remote task_work to preserve completion context.
- FD messages transfer a source fixed file from the sender into the target ring fixed-file table, optionally posting a notification CQE.
- Cross-ring locking uses trylock for inline source-locked paths; failure returns `-EAGAIN` so io-wq can retry without lock inversion.
- `io_msg_ring_cleanup()` drops grabbed source files if an FD transfer request is abandoned.
- `io_uring_sync_msg_ring()` supports synchronous data-only delivery to an io_uring fd.

Important details:
- Target rings disabled with `IORING_SETUP_R_DISABLED` reject messages.
- Sending an fd to the same ring is rejected.
- If target CQE posting fails after FD install, sender receives `-EOVERFLOW` but the target file was already installed.
