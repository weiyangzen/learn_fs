# File Research: sources/os/linux/linux-stable/fs/dlm/lockspace.c

## Purpose
`lockspace.c` manages DLM lockspace lifecycle: global registration, sysfs control, userspace coordination through uevents, creation, lookup/refcounting, release, and forced stopping when the control daemon disappears.

## Sysfs and Uevents
Each lockspace is represented by a kobject under the `dlm` kset. Attributes include:
- `control`: `0` stops a lockspace, `1` starts it.
- `event_done`: written by userspace control daemon to complete group events.
- `id`: lockspace global id.
- `nodir`: enables no-directory mode.
- `recover_status`: current recovery status bits.
- `recover_nodeid`: current recovery node id for diagnostics.

`do_uevent()` emits online/offline kobject events and waits for `dlm_controld` to write `event_done`. `dlm_uevent()` adds the `LOCKSPACE=<name>` environment variable.

## Global State
The file maintains:
- `ls_count`: number of created lockspaces.
- `ls_lock`: serializes create/release and midcomms start/stop.
- `lslist` plus `lslist_lock`: global lockspace list and lookup/refcount protection.

Lookup helpers:
- `dlm_find_lockspace_global()`
- `dlm_find_lockspace_local()`
- `dlm_find_lockspace_device()`
- `dlm_put_lockspace()`

## Creation
`dlm_lockspace_init()` creates the `dlm` kset. `new_lockspace()` validates name/LVB length, requires the user daemon, checks cluster-name compatibility when recovery callbacks are enabled, reuses existing lockspaces unless `DLM_LSFL_NEWEXCL` is set, then allocates and initializes `struct dlm_ls`.

Initialization covers RSB hash table, LKB xarray, waiters/orphans, member lists, recovery queues, recovery buffer, scan timer, masters/directory-dump lists, callback workqueue, recoverd thread, sysfs kobject, userspace join uevent, initial recovery completion, and debugfs files.

`__dlm_new_lockspace()` starts global midcomms on the first lockspace and shuts it down if creation fails. `dlm_new_lockspace()` forces filesystem-user mode; `dlm_new_user_lockspace()` rejects softirq mode for userspace.

## Release
`lockspace_busy()` checks whether locks remain, depending on release option. `release_lockspace()` decrements create count or removes the final instance, sends leave uevents when appropriate, stops recoverd/callbacks/timers, deregisters the user device, clears members, purges requestqueue/recovery state, removes debugfs/sysfs, and queues delayed memory cleanup through `free_lockspace()` on `dlm_wq`.

`free_lockspace()` destroys remaining LKBs and RSBs after delayed teardown.

`dlm_release_lockspace()` validates release option, finds the lockspace, serializes release, decrements `ls_count`, and stops midcomms when the last lockspace is gone.

## Emergency Stop
`dlm_stop_lockspaces()` scans running lockspaces and calls `dlm_ls_stop()` if the userspace daemon has gone away, logging any lockspaces left stopped.

## Dependencies
Integrates with midcomms, recoverd, recovery, membership, config, memory allocation, user device, requestqueue, debugfs, AST callbacks, and lock engine timers.

## Risks and Notes
Lockspace creation and release cross kernel threads, sysfs, uevents, timers, midcomms, and userspace daemon state. The teardown order is deliberate: stop external activity first, remove from global list only after references drain, then free heavy state asynchronously.
