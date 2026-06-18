# File Research: sources/os/linux/linux-stable/fs/autofs/waitq.c

## Purpose
Implements autofs daemon notification and wait-queue coordination for mount and expire requests.

## Main Interfaces
- `autofs_wait()`.
- `autofs_wait_release()`.
- `autofs_catatonic_mode()`.

## Important Behavior
`autofs_wait()` builds a request name, validates whether a wait should continue, reuses an existing wait for duplicate requests, or creates a new `autofs_wait_queue` with token, requester uid/gid, pid/tgid translated into the daemon pid namespace, and device/inode metadata. It then sends the appropriate protocol v4 or v5 packet to the daemon pipe and waits killably until userspace releases the token.

`autofs_notify_daemon()` formats missing/expire packets for protocol v4 or v5 and writes them to the packet pipe. Pipe write failure can release the wait with an error or force catatonic mode. `autofs_wait_release()` unlinks the wait by token, frees the saved name, records status, and wakes all waiters.

`autofs_catatonic_mode()` marks the mount unresponsive, releases all queued waits with `-ENOENT`, closes the daemon pipe, and resets pipe state.

## State And Synchronization
`wq_mutex` protects the wait queue list and daemon notification setup. `pipe_mutex` serializes writes. Wait entries use a `wait_ctr` convention to keep the object alive for both list ownership and sleeping tasks.

## Risks / Review Notes
The request name buffer stores an offset so the exact allocation can be freed after using a shifted `qstr.name`. Namespace translation failure rejects requests from unrelated pid namespaces. Catatonic mode is the central failure/shutdown escape path and must wake all blocked waiters.
