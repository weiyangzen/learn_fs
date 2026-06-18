# sources/user-network-fs/samba/source4/ntvfs/common/notify.c

## Purpose

`notify.c` implements Samba source4's shared change-notify database for NTVFS. It records directory change-notify waiters in a cluster-capable temp DB, integrates optional OS-level notification backends, and sends matching events back to waiting server instances over imessaging.

## Important APIs, Types, and Functions

Public APIs are `notify_init()`, `notify_add()`, `notify_remove()`, and `notify_trigger()`. Internal structures include `struct notify_context` and `struct notify_list`. Important helpers include `notify_load()`, `notify_save()`, `notify_add_array()`, `notify_remove_all()`, `notify_send()`, `notify_handler()`, `sys_notify_callback()`, `notify_lock()`, and `notify_unlock()`.

## Control Flow

Initialization honors share option `notify:enable`, opens the `notify` cluster temp DB with sequence numbers, registers `MSG_PVFS_NOTIFY`, and creates a sys-notify context. Adding a watch locks the DB, loads the cached NDR `notify_array` if the sequence changed, normalizes trailing `/.`, records an in-memory callback, lets sys-notify consume supported filter bits, and stores remaining filters in the shared array by path depth. Triggering reloads if needed, walks path depths, skips depths whose aggregate masks cannot match, uses binary search in sorted entries for candidate paths, and sends matching events through imessaging.

## State and Persistence Behavior

Runtime persistent state is the shared `NOTIFY_KEY` record in `notify.tdb`, NDR-encoded as `struct notify_array`. Local state includes callback list entries and sys-notify handles. The destructor deregisters messaging and removes all entries for the local server from the DB.

## Dependencies and Integration Points

It depends on dbwrap, NDR notify structures, imessaging, cluster server IDs, sys-notify backends, share options, talloc sorting, and util TDB helpers. Filesystem backends call `notify_add()` for change notify requests and `notify_trigger()` when filesystem events occur.

## Risks and Edge Cases

The fast path is subtle: path length calculations use pointer differences while iterating slash positions, so boundary cases matter. `notify_handler()` matches incoming events by `private_data` pointer, which is only meaningful for the target process that registered it. If sys-notify handles some but not all filters, the remaining filters must be stored correctly or events are lost. DB corruption in NDR decode disables notification loading for that trigger.

## Test Signals

Tests should cover disabled notify, add/remove at multiple depths, trailing `/.` normalization, recursive versus non-recursive filters, sys-notify partial handling, trigger path boundary cases, sequence-number cache refresh, messaging callback delivery, destructor cleanup, and many watchers sorted by path.
