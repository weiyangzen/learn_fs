# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_fsevents.c

## Scope

This file implements the kernel side of `/dev/fsevents` when `CONFIG_FSE` is enabled, plus fallback stubs when disabled. It creates and coalesces filesystem events, manages watcher queues, serializes event copyout, supports kqueue/select/read/ioctl interfaces, handles unmount-pending notifications, and exposes helper functions used by other VFS code.

## Public And Internal APIs Covered

- Event creation/filtering: `need_fsevent()`, `add_fsevent()`, `test_fse_access_granted()`, `create_fsevent_from_kevent()`.
- Event metadata helpers: `get_pathbuff()`, `release_pathbuff()`, `get_fse_info()`, `vnode_get_fse_info_from_vap()`.
- Watcher management: `add_watcher()`, `remove_watcher()`, `watcher_add_event()`, `fmod_watch()`.
- Device/file operations: `fseventsopen()`, `fseventsclose()`, `fseventsread()`, `fseventswrite()`, `fseventsioctl()`, `fseventsf_read()`, `fseventsf_ioctl()`, `fseventsf_select()`, `fseventsf_close()`, `fseventsf_kqfilter()`, `fseventsf_drain()`.
- Initialization: `fsevents_init()` and `fsevents_internal_init()`.
- Unmount coordination: `fsevent_unmount()`.

## Control Flow And Behavior

Initialization creates an exhaustible `kfs_event` zone, fills it to `kern.maxkfsevents`, clears watcher state, installs the character device, and creates `/dev/fsevents`.

`add_fsevent()` validates event type and watcher interest, coalesces repeated same-process events within about one second, allocates one or two `kfs_event` objects for normal or two-path operations, parses variadic event arguments, captures vnode attributes/path strings, marks dropped-data flags when needed, and queues the event to interested watchers. Special cases handle document-id events, activity events, access-granted events, and unmount-pending events. Hardlink-sensitive events may be replicated for sibling links using APFS next-link lookup and `fsgetpath_internal()`.

Watchers are created through the clone ioctl, which copies an event-interest array, allocates an `fsevent_handle`, registers a watcher, allocates a file descriptor, and attaches `fsevents_fops`. Watcher queueing increments event references, uses a ring buffer, wakes readers immediately past thresholds, or schedules a delayed thread-call wakeup. Non-entitled/non-system watchers that fall too far behind have queued events dropped and receive `FSE_EVENTS_DROPPED`.

`fmod_watch()` serializes readers, sleeps when no events are queued, emits dropped-event markers first, copies events into the caller `uio`, and releases event references as queue entries are consumed. `copy_out_kfse()` emits typed argument records for regular, compact, document-id, activity, access-granted, and two-path events.

`fseventswrite()` accepts externally written serialized events, parses them in a permanent 4 KiB staging buffer, preserves incomplete records across chunk boundaries, and reinjects parsed events through `add_fsevent()`.

## State And Data Structures

- `kfs_event` stores event type, flags, refcount, timestamp, pid, and union payloads for regular, document-id, activity, and access-granted events.
- `fs_event_watcher` stores interest array, excluded devices, ring queue, read/write indexes, flags, max event id, process identity, and handle pointer.
- Global state includes watcher table, per-event watcher counts, outstanding-event list, pending rename count, event zone, unmount ack state, coalescing cache, and delayed delivery timer.
- Locks: `event_handling_lock`, `watch_table_lock`, `event_buf_lock`, and `event_writer_lock`.

## Dependencies

Depends on VFS vnode attributes/path lookup, name cache string table, kqueue/select/fileproc APIs, devfs char devices, kauth credentials, IOKit entitlements, audit tokens, APFS hardlink ioctl support, sysctl/PE boot defaults, thread calls, zones, and user `uio` copy helpers.

## Risks And Invariants

- Event objects are refcounted across global lists and watcher queues; `release_event_ref()` must remove list entries and string-table names exactly once.
- The event zone is exhaustible; allocation failure marks all watchers as having dropped events and throttles diagnostics.
- `KFSE_BEING_CREATED` prevents copyout of partially built events.
- Reader serialization uses `num_readers`; close/drain paths wait and wake sleepers before teardown.
- Watcher entitlement filtering silently removes restricted event interests for activity and access-granted events.
- Non-Apple watchers are intentionally filtered for certain system directories and are penalized if they fall behind.
- Fallback `CONFIG_FSE` stubs still provide path buffer allocation and no-op `add_fsevent()`/`need_fsevent()` so other VFS code can compile without feature conditionals.
