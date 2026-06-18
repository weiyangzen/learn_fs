# File Research: sources/os/linux/linux-stable/fs/ecryptfs/miscdev.c

## Summary
Implements the eCryptfs misc character device `/dev/ecryptfs`, used for kernel-to-userspace daemon messaging.

## Main Responsibilities
- Registers and deregisters the misc device.
- Opens one daemon channel per effective UID.
- Queues kernel requests to the daemon and wakes daemon readers.
- Parses daemon responses, hello, and quit packets.
- Handles daemon poll, read, write, and release operations.

## Key APIs
- `ecryptfs_send_miscdev()`
- `ecryptfs_init_ecryptfs_miscdev()`
- `ecryptfs_destroy_ecryptfs_miscdev()`

## Important Behavior
Outgoing messages are stored as `ecryptfs_msg_ctx` entries on `daemon->msg_ctx_out_queue`. `read()` formats queued messages as packet type, big-endian counter, optional encoded length, and optional `struct ecryptfs_message`.

Incoming `write()` validates packet size, parses the encoded message length, copies the user buffer, and dispatches `ECRYPTFS_MSG_RESPONSE` to `ecryptfs_process_response()`.

## Risks
Daemon lifetime depends on flags such as `ECRYPTFS_DAEMON_MISCDEV_OPEN`, `ECRYPTFS_DAEMON_IN_READ`, and `ECRYPTFS_DAEMON_ZOMBIE` under two mutex domains. Packet-size validation is central because data crosses directly from userspace into kernel response handling.
