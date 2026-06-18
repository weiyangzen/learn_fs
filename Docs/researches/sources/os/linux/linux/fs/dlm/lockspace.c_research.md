# File Research: sources/os/linux/linux/fs/dlm/lockspace.c

## Role

`lockspace.c` manages DLM lockspace lifetime. It creates/destroys lockspaces, tracks them globally, starts/stops global DLM communication threads, integrates with sysfs and uevents, initializes per-lockspace data structures, and coordinates final cleanup.

## Global State

The file maintains:

- `ls_count`: number of active lockspaces.
- `ls_lock`: mutex serializing create/release operations.
- `lslist`: global list of lockspaces.
- `lslist_lock`: spinlock protecting `lslist` and create counts.
- `dlm_kset`: sysfs kset under kernel kobject for DLM lockspaces.

## Sysfs Attributes

Each lockspace kobject exposes:

- `control` write-only: `0` calls `dlm_ls_stop()`, `1` calls `dlm_ls_start()`.
- `event_done` write-only: stores the userspace group-management result and wakes waiters.
- `id` read/write: lockspace global id.
- `nodir` read/write: exposes and can set no-directory mode.
- `recover_status` read-only: current recovery status bits.
- `recover_nodeid` read-only: recovery nodeid for diagnostics.

Attributes are wired through `struct dlm_attr`, `dlm_attr_show()`, `dlm_attr_store()`, and `dlm_ktype`.

## Uevent Flow

`do_uevent()` sends:

- `KOBJ_ONLINE` when joining a lockspace.
- `KOBJ_OFFLINE` with `RELEASE_RECOVER=<value>` when leaving.

It then waits until userspace, normally `dlm_controld`, writes `event_done`, which sets `LSFL_UEVENT_WAIT` and wakes `ls_uevent_wait`.

`dlm_uevent()` adds `LOCKSPACE=<name>` to the uevent environment.

## Lockspace Lookup and References

- `dlm_find_lockspace_global(uint32_t id)` finds by global id and increments `ls_count`.
- `dlm_find_lockspace_local(dlm_lockspace_t *lockspace)` treats the pointer as `struct dlm_ls *` and increments `ls_count`.
- `dlm_find_lockspace_device(int minor)` finds by miscdevice minor.
- `dlm_put_lockspace()` decrements `ls_count` and wakes `ls_count_wait` when the transient reference count reaches zero.

`remove_lockspace()` waits for transient users to drain, then removes the lockspace from `lslist`.

## Creation Flow

`dlm_lockspace_init()` initializes global state and creates the `dlm` kset. `threads_start()` starts midcomms when the first lockspace is created.

`new_lockspace()` performs the real setup:

1. Validate name length and LVB length alignment.
2. Pin the module.
3. Require the DLM userspace daemon.
4. Validate optional recovery callback support and cluster name.
5. Reuse an existing lockspace by name unless `DLM_LSFL_NEWEXCL` forbids it.
6. Allocate and initialize `struct dlm_ls`.
7. Initialize resource table, xarrays, queues, wait queues, locks, recovery buffers, member lists, scan timer, and debug fields.
8. Add the lockspace to `lslist`.
9. Start callback and recoverd infrastructure.
10. Wait until recoverd holds the initial recovery lock.
11. Add the sysfs kobject and emit add/join events.
12. Wait for initial recovery completion.
13. Create debugfs files and return the lockspace pointer.

Error unwinding stops recoverd/callbacks, removes list membership, frees recovery buffers and xarrays, destroys the rhashtable, drops the kobject/module reference, and frees memory as appropriate.

`__dlm_new_lockspace()` serializes global creation with `ls_lock`, starts midcomms for the first lockspace, and shuts it back down if creation fails. `dlm_new_lockspace()` forces `DLM_LSFL_FS` for kernel/filesystem users. `dlm_new_user_lockspace()` rejects `DLM_LSFL_SOFTIRQ` and creates a userspace lockspace.

## Release Flow

`lockspace_busy()` checks the LKB xarray to decide whether release is allowed for `DLM_RELEASE_NO_LOCKS` or `DLM_RELEASE_UNUSED`.

`release_lockspace()`:

- Updates `ls_create_count` under `lslist_lock`.
- Waits for midcomms version synchronization when releasing the last lockspace.
- Deregisters the userspace device.
- Optionally emits the leave uevent.
- Stops recoverd.
- Clears running state and shuts down the scan timer.
- Clears members and shuts down midcomms if this is the last lockspace.
- Stops callbacks.
- Removes the lockspace from the global list.
- Deletes debugfs files.
- Drops sysfs kobject state.
- Destroys recovery xarray and buffers.
- Purges request queues, recovery args, members, gone members, and node array.
- Queues delayed freeing on `dlm_wq` through `free_lockspace()`.
- Drops the module reference.

`dlm_release_lockspace()` validates the release option, takes a local reference, serializes with `ls_lock`, calls `release_lockspace()`, decrements global lockspace count, and stops midcomms when no lockspaces remain.

## Final Free

`free_lockspace()` runs asynchronously. It frees all LKBs still in `ls_lkbxa`, destroys the xarray, frees all RSBs in the rhashtable via `rhashtable_free_and_destroy()`, and finally frees the `struct dlm_ls`.

The delayed free avoids tearing down structures while prior asynchronous cleanup and kobject release paths may still be unwinding.

## Emergency Stop

`dlm_stop_lockspaces()` iterates all lockspaces and calls `dlm_ls_stop()` on any still running lockspace when the userspace control daemon is unavailable. It restarts iteration after each stop because the list can change.

## Dependencies

This file coordinates with:

- `midcomms` for global communication start/shutdown/stop.
- `recoverd` and `recover` for recovery thread lifecycle and initial recovery.
- `member` for membership cleanup.
- `requestqueue`, `ast`, and `user` for per-lockspace runtime cleanup.
- `dir` and `lock` for initialized fields and scan timer callback.
- Linux module, kobject, kset, sysfs, waitqueue, xarray, rhashtable, timer, and workqueue APIs.

## Research Notes

`lockspace.c` is the owner of `struct dlm_ls` allocation and destruction, but it deliberately does not own most lock behavior. Its main invariants are serialized create/release through `ls_lock`, list/ref safety through `lslist_lock` and `ls_count_wait`, initial recovery lock acquisition before exposing the lockspace, and delayed final free after all DLM runtime components have been stopped.
