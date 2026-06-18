# File Research: sources/virtualization/libnbd/lib/disconnect.c

Implements synchronous shutdown and async disconnect queuing.

Key functions:
- `nbd_unlocked_shutdown`: gracefully aborts option mode if negotiating, optionally abandons pending commands, queues disconnect if ready/processing, then polls until CLOSED or DEAD.
- `nbd_unlocked_aio_disconnect`: queues `NBD_CMD_DISC` through `nbd_internal_command_common` and marks `disconnect_request`.

Interactions:
- Uses option abort from `opt.c`.
- Uses command queue abort helper from generated state code.
- Uses polling and state predicates.

Research notes:
- `NBD_CMD_DISC` has no server reply, so the command remains in-flight until close/dead cleanup and no public completion cookie is returned.
- `LIBNBD_SHUTDOWN_ABANDON_PENDING` only aborts commands not yet sent to the server.
