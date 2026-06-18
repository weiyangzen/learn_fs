# File Research: sources/os/linux/linux-stable/fs/notify/fanotify/fanotify.c

Purpose: Core fanotify event creation, filtering, merging, permission-response waiting, and destruction logic for the fsnotify backend.

Core helper groups:
- Identity and hash helpers compare and hash paths, fsids, file handles, name-event info, fid events, and filesystem error events.
- Merge helpers decide when queued events can be coalesced.
- Permission helpers wait for userspace responses to access-permission events.
- Event-mask helpers calculate which event bits a group should receive after mark masks and ignore masks are applied.
- File-handle helpers encode exportfs file handles for FID-style fanotify events.
- Allocation helpers create the different event object variants.
- Free helpers release resources for every event type and group/mark private state.

Important behavior:
- `fanotify_should_merge()` only merges events with the same hash, type, and pid, and refuses to merge directory and non-directory events or rename/non-rename combinations. It delegates equality by event type: path, fid, name, filesystem error, or mount event.
- `fanotify_merge()` limits merge scanning to `FANOTIFY_MAX_MERGE_EVENTS` and never merges permission events. For filesystem error events it increments `err_count` on merge.
- `fanotify_get_response()` waits on `access_waitq` for permission events, handles signal cancellation and races with userspace replies, converts `FAN_ALLOW`/`FAN_DENY` plus optional errno to kernel return values, audits when requested, and destroys the permission event before returning.
- `fanotify_group_event_mask()` combines all matching marks, applies ignore masks, enforces mode-specific requirements such as path availability, FID/dir availability, or mount-event type, and strips/report flags according to legacy vs FID modes.
- `fanotify_encode_fh_len()` and `fanotify_encode_fh()` use exportfs file handles for FID reports, support inline or external handle storage, hash handle contents for merge keys, and fall back to invalid file handles on encoding failure.
- `fanotify_alloc_event()` selects event representation based on mask and group flags: permission path events, filesystem error events, name events, FID events, path events, or mount events. It charges allocation to the monitoring group memcg and uses stronger allocation flags for unlimited queues.
- `fanotify_handle_event()` is the fsnotify callback. It validates compile-time mask equality with `BUILD_BUG_ON`, filters the event mask, prepares permission waits when needed, obtains fsid in FID mode, allocates the event, queues/merges it through fsnotify, waits for permission responses, and finalizes permission waits.
- `fanotify_free_event()` dispatches destruction based on event type and releases paths, pids, external file-handle buffers, kmem-cache objects, mempool error events, or heap allocations as appropriate.

Event model details:
- Path events hold a `struct path` and take a path reference.
- Permission events are path events with response state, optional range information, and wait semantics.
- FID events hold fsid plus an encoded object file handle.
- Name events can include directory file handle, second directory file handle for rename, child file handle, and one or two names in a variable-sized allocation.
- Filesystem error events use a mempool and may carry an invalid file handle when the error has no inode.
- Mount events carry a mount ID and are explicitly not mergeable.

Dependencies and interfaces:
- Implements `const struct fsnotify_ops fanotify_fsnotify_ops` with `.handle_event`, `.free_group_priv`, `.free_event`, `.freeing_mark`, and `.free_mark`.
- Uses fsnotify backend iteration, queueing, mark mask, wait, and overflow APIs.
- Uses exportfs for file-handle encoding, audit for permission response auditing, memcg charging, ucounts, and fanotify-local structures declared in `fanotify.h`.

Concurrency and lifetime:
- Event queue and merge hash operations assume `group->notification_lock` where required.
- Permission events have explicit state transitions: init, reported, canceled, answered.
- Mark and group resource accounting is released through the fsnotify ops callbacks.
- Allocation paths take references to paths and pids and release them in the matching free helpers.

Design notes and risks:
- The file is central fanotify machinery; small mask/filter changes can affect userspace ABI behavior.
- FID/name event layout is variable-sized and depends on exact ordering of encoded handles and names through `fanotify_info_*` helpers.
- Permission event handling is security-sensitive: failures to allocate permission events deny access by returning `-ENOMEM`, while races with mark deletion intentionally allow the operation.
- The compile-time `BUILD_BUG_ON(HWEIGHT32(ALL_FANOTIFY_EVENT_BITS) != 24)` is a guard that must be updated when event bit definitions change.
