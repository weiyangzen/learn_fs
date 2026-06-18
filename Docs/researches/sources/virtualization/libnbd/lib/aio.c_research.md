# File Research: sources/virtualization/libnbd/lib/aio.c

Implements async-facing helpers for file descriptor access, readiness notification, command completion, and in-flight count tracking.

Key functions:
- `nbd_internal_retire_and_free_command`: releases command callbacks and any block-status filter id vector, then frees the command.
- `nbd_unlocked_aio_get_fd`: returns the transport fd through socket ops, failing if not connected.
- `nbd_unlocked_aio_notify_read` / `nbd_unlocked_aio_notify_write`: feed external readiness events into the generated state machine.
- `nbd_unlocked_aio_command_completed`: finds a completed command by cookie, validates read byte coverage, unlinks it from `cmds_done`, frees it, and reports success or command error.
- `nbd_unlocked_aio_peek_command_completed`: returns the oldest completed command cookie without retiring it.
- `nbd_unlocked_aio_in_flight`: returns queued plus issued command count.

Interactions:
- Uses command queues in `struct nbd_handle`.
- Calls `nbd_internal_run` with `notify_read`/`notify_write`.
- Uses protocol names from `protocol.c` for error messages.

Research notes:
- Read completion treats short structured reads as `EPROTO` unless the server already reported an error.
- Disconnect commands are deliberately excluded from public completion tracking.
