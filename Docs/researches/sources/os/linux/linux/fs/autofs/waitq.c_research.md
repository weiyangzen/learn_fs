# File Research: sources/os/linux/linux/fs/autofs/waitq.c

## Summary
Implements autofs wait queues and daemon notification through the autofs control pipe.

## Main Responsibilities
- Enter catatonic mode and wake/fail all pending waits.
- Write mount/expire request packets to the daemon pipe.
- Deduplicate waits for the same path.
- Validate whether a wait is still needed after races.
- Sleep until daemon releases a wait token.
- Release wait tokens from root or device ioctls.

## Key APIs
- `autofs_wait()`.
- `autofs_wait_release()`.
- `autofs_catatonic_mode()`.

## Important Behavior
Each new wait gets a global nonzero token. Requests are keyed by a `qstr` derived from either the raw dentry path or a dummy direct-mount root name.

Protocol v4 and v5 use different packet formats. v5 packets include dev, ino, uid, gid, pid, and tgid translated into the daemon’s namespaces.

`autofs_notify_daemon()` drops `wq_mutex` while writing to the pipe. Write failures either release the specific wait for recoverable errors or put the mount into catatonic mode.

`validate_request()` handles important races: an existing wait, a completed mount while sleeping, an expire wait whose queue is not yet posted, and invalid negative dentries for direct/offset/non-root indirect cases.

After a successful mount wait, requester uid/gid are stored into the relevant `autofs_info` for daemon restart/reconnect use.

## Risks
Wait queue lifetime uses `wait_ctr` because both waiters and release paths can hold references. The code depends on `wq->name.name == NULL` as the wake condition. Pipe write error handling and catatonic transition must avoid lost wakeups and dangling pipe refs.
