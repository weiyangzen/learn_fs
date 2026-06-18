# File Research: sources/os/linux/linux/fs/ecryptfs/messaging.c

## Purpose
Implements the in-kernel request/response context pool and daemon registry used by eCryptfs userspace messaging, mainly for public-key operations through `ecryptfsd`.

## Main Responsibilities
- Maintain free and allocated message context lists.
- Maintain a hash table of connected daemons keyed by current effective UID.
- Allocate message contexts for outbound requests.
- Deliver daemon responses to waiting kernel tasks by context index and sequence counter.
- Initialize and release messaging state and the eCryptfs misc device.

## Message Context Flow
`ecryptfs_send_message()` locks the daemon hash, finds the daemon for the current effective UID, obtains a free `ecryptfs_msg_ctx`, moves it from free to allocated, increments its sequence counter, unlocks it, and sends data through `ecryptfs_send_miscdev()`.

`ecryptfs_wait_for_response()` sleeps interruptibly until the context state becomes done or timeout expires. On success it transfers the response message pointer to the caller. In all cases it returns the context to the free list.

`ecryptfs_process_response()` validates the response context index, locks the target context, checks that it is pending and sequence matches, duplicates the message, marks the context done, and wakes the waiting task.

## Daemon Registry
`ecryptfs_spawn_daemon()` allocates and initializes an `ecryptfs_daemon`, stores the miscdev file, initializes its outbound queue/waitqueue, and inserts it into the per-euid hash bucket.

`ecryptfs_find_daemon_by_euid()` searches the current effective UID bucket and matches against daemon file credentials.

`ecryptfs_exorcise_daemon()` refuses to destroy daemons currently in read or poll, drops queued outbound messages back to the free list, removes the daemon from the hash, and frees it with sensitive cleanup.

## Initialization and Teardown
`ecryptfs_init_messaging()` clamps user count, derives hash size, allocates and initializes daemon buckets, allocates the fixed message context array, initializes each context and free-list node, then initializes the misc device.

`ecryptfs_release_messaging()` frees pending response messages, frees the context array, walks daemon buckets and destroys daemons, frees the daemon hash, and destroys the misc device.

## State and Locking
- `ecryptfs_msg_ctx_lists_mux` protects free/allocated context lists.
- Each `ecryptfs_msg_ctx` has its own mutex.
- `ecryptfs_daemon_hash_mux` protects daemon hash access.
- Each daemon has a mutex for flags and outbound queue state.

## Error Handling and Edge Cases
- Empty context pool returns `-ENOMEM` and logs a hint to increase `ecryptfs_message_buf_len`.
- Missing daemon returns `-ENOTCONN`.
- Wait timeout returns `-ENOMSG`.
- Invalid response indexes, states, or sequence numbers return `-EINVAL`.
- Teardown logs and continues if daemon destruction fails.

## Risks and Notes
- Hash macro ignores its `uid` parameter and uses `current_euid()` directly.
- The fixed context pool bounds memory use but can throttle public-key operations.
- Correctness relies on miscdev code, not in this file, to call spawn/exorcise/send/process functions under expected locking.
