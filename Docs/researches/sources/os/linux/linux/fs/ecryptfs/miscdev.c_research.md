# File Research: sources/os/linux/linux/fs/ecryptfs/miscdev.c

Implements the `/dev/ecryptfs` miscdevice used for kernel-to-userspace eCryptfs daemon messaging.

Key behavior:
- Tracks daemon device opens with `ecryptfs_num_miscdev_opens`.
- `open` finds or spawns the daemon for the caller euid, marks `ECRYPTFS_DAEMON_MISCDEV_OPEN`, and stores the daemon in `file->private_data`.
- `poll` reports readable state when `msg_ctx_out_queue` is non-empty, while guarding against zombie, concurrent read, and concurrent poll states.
- `release` clears the miscdev-open flag, decrements the open count, and calls `ecryptfs_exorcise_daemon()`.
- `ecryptfs_send_miscdev()` packages an `ecryptfs_message`, links the message context onto the daemon outbound queue, increments the queued count, and wakes waiters.
- `read` blocks until a queued message exists, serializes packet type, big-endian counter, optional packet length, and optional message body to userspace, then frees or retains the message context depending on whether a reply is expected.
- `write` validates userspace packet lengths, copies the packet, accepts HELO/QUIT, and dispatches RESPONSE packets to `ecryptfs_process_response()`.
- Registers and deregisters a dynamic-minor miscdevice named `ecryptfs`.

Important interactions:
- Depends on daemon lifecycle and message-context helpers from the rest of eCryptfs.
- The packet format is a small framing layer around `struct ecryptfs_message` plus daemon sequence numbers.
- Module teardown asserts no miscdevice opens remain before deregistration.
