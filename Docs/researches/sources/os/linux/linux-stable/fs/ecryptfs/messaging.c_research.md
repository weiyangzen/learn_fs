# File Research: sources/os/linux/linux-stable/fs/ecryptfs/messaging.c

## Summary
Implements the in-kernel messaging core used to communicate with per-user ecryptfsd daemons through the miscdevice layer. It manages daemon registration lookup, fixed message-context pools, request sequencing, response delivery, wait/timeout behavior, and messaging teardown.

## Main Responsibilities
- Maintain free and allocated lists of `ecryptfs_msg_ctx` objects.
- Maintain a hash table of ecryptfsd daemon objects keyed by current effective UID.
- Allocate a free message context for outbound requests and assign monotonically increasing counters.
- Queue outbound messages to the matching daemon through `ecryptfs_send_miscdev()`.
- Process userspace responses by validating context index, pending state, and sequence counter.
- Wake the sleeping requester when a response arrives.
- Wait for responses with `ecryptfs_message_wait_timeout`.
- Initialize and release message context arrays, daemon hash buckets, and the miscdevice layer.
- Destroy live daemon objects and pending messages during teardown.

## Key APIs
- `ecryptfs_spawn_daemon()`
- `ecryptfs_exorcise_daemon()`
- `ecryptfs_find_daemon_by_euid()`
- `ecryptfs_send_message()`
- `ecryptfs_wait_for_response()`
- `ecryptfs_process_response()`
- `ecryptfs_init_messaging()`
- `ecryptfs_release_messaging()`

## Important Behavior
Each outbound request reserves a context from a fixed-size pool. Responses must reference a valid context index and match the current sequence counter, preventing stale or misrouted userspace replies from completing the wrong request.

Daemon lookup is by effective UID. If no daemon exists for the current euid, sending returns `-ENOTCONN`. If no context is free, sending fails with `-ENOMEM` and recommends increasing `ecryptfs_message_buf_len`.

`ecryptfs_wait_for_response()` uses interruptible timeout sleeps and always moves the context back to the free list before returning. Successful callers receive ownership of the copied response message.

## Research Notes
This file backs public-key FEK encryption/decryption paths in `keystore.c`. Its main invariants are list locking order, context state transitions, daemon hash locking, sequence matching, and cleaning queued messages when daemons disappear.
