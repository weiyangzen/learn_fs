# File Research: sources/os/linux/linux/fs/notify/fanotify/fanotify.c

Purpose: Core fanotify backend logic for event filtering, allocation, merging, permission-response waiting, event destruction, and fsnotify operation hooks.

Core helper groups:
- Equality/hash helpers compare paths, fsids, file handles, FID events, name events, filesystem error events, and mount events.
- Merge helpers decide whether queued events can coalesce.
- Permission helpers wait for userspace access decisions.
- Event-mask helpers combine mark masks and ignore masks into outgoing user-visible fanotify masks.
- File-handle helpers encode exportfs file handles for FID-style reporting.
- Allocation/free helpers create and destroy path, permission, FID, name, filesystem-error, overflow, and mount event variants.

Important behavior:
- `fanotify_should_merge()` requires matching hash, event type, and pid, refuses directory/non-directory mixing, refuses rename/non-rename mixing, and then compares event-specific identity.
- `fanotify_merge()` scans at most `FANOTIFY_MAX_MERGE_EVENTS`, never merges permission events, and increments filesystem error counts on merged error events.
- `fanotify_get_response()` waits for permission event replies, handles signal cancellation, converts `FAN_ALLOW`/`FAN_DENY` plus optional errno to kernel returns, audits requested responses, and destroys the permission event.
- `fanotify_group_event_mask()` applies mark masks, ignore masks, fid/path/mount mode constraints, and strips/report flags according to legacy versus FID reporting mode.
- `fanotify_encode_fh_len()` and `fanotify_encode_fh()` use `exportfs_encode_fid()` and support inline or external file-handle storage; encode failures produce invalid handles for report fallback.
- `fanotify_alloc_event()` selects representation based on mask and group flags: permission path event, filesystem error event, name event, FID event, path event, or mount event.
- `fanotify_handle_event()` validates fanotify/fsnotify mask alignment with `BUILD_BUG_ON`, filters the event, prepares permission waits, obtains fsid for FID mode, allocates, queues/merges, waits for permission responses when needed, and finalizes waits.
- `fanotify_free_event()` dispatches cleanup by event type and releases paths, pids, external buffers, kmem-cache objects, mempool objects, or heap allocations.

Event model details:
- Path events store and refcount a `struct path`.
- Permission events are path events with response state, optional range info, and wait semantics.
- FID events store fsid plus encoded object file handle.
- Name events can store directory file handle, second directory file handle for rename, child file handle, and one or two names in a variable-sized allocation.
- Filesystem error events use a mempool and may carry an invalid file handle when no inode exists.
- Mount events carry a mount ID and are not mergeable.

Dependencies and interfaces:
- Implements `const struct fsnotify_ops fanotify_fsnotify_ops`.
- Uses fsnotify iteration, queueing, marks, wait handling, and overflow APIs.
- Uses exportfs, audit, memcg charging, ucounts, and fanotify-local definitions from `fanotify.h`.

Concurrency and lifetime:
- Queue merge hash insertion assumes `group->notification_lock`.
- Permission events transition through init, reported, canceled, and answered states.
- Mark and group resource accounting is released through fsnotify ops callbacks.
- Allocation paths take path and pid references and release them in paired free helpers.

Design notes and risks:
- Central fanotify machinery with direct userspace ABI impact.
- Permission handling is security-sensitive: permission event allocation failure denies access, while mark-deletion races intentionally allow the operation.
- Variable-sized name/FID event layout depends on exact helper ordering and size calculations.
- `BUILD_BUG_ON(HWEIGHT32(ALL_FANOTIFY_EVENT_BITS) != 24)` must be updated with event bit definition changes.
