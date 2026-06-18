# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_subr.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-10231, source bytes 262134, report `Docs/researches/chunks/chunk_sources_os_darwin_xnu_bsd_vfs_vfs_subr_c_1_1_10231_605ae2fbb88b_research.md`
- chunk 2: lines 10232-13491, source bytes 83822, report `Docs/researches/chunks/chunk_sources_os_darwin_xnu_bsd_vfs_vfs_subr_c_2_10232_13491_40d0f45d4e4a_research.md`

## Chunk Research

### Chunk 1: lines 1-10231

# Chunk Research: sources/os/darwin/xnu/bsd/vfs/vfs_subr.c lines 1-10231

## Scope

This chunk covers the first 10,231 lines of Darwin XNU's `bsd/vfs/vfs_subr.c`, within subset A (`sources/os/darwin/xnu`). It is the first chunk of a larger file; it stops inside `vnode_authorize_callback_int()` immediately after initializing the local authorization context and extracting `cred = ctx->vc_ucred`. Later authorization completion, authattr helpers, triggers, leases, and other tail code are cross-chunk material.

## Purpose

This chunk implements most core VFS/vnode support outside filesystem-specific VNOPs: vnode table initialization, mount/root boot and root switching, mount iteration and reference draining, vnode allocation/reuse/reclaim, device vnode aliasing, name/path helper APIs, VFS sysctl and kqueue events, basic vnode lookup/open/close helpers, object creation, and the first half of vnode authorization.

## APIs and Entry Points

- Initialization and globals: `vntblinit()`, global vnode lists (`vnode_free_list`, `vnode_dead_list`, `vnode_async_work_list`, `vnode_rage_list`), mount list (`mountlist`), vnode counters, telemetry (`freeable_vnodes`), SMR setup, worker-thread startup.
- Write and buffer state: `vnode_waitforwrites()`, `vnode_startwrite()`, `vnode_writedone()`, `vnode_hasdirtyblks()`, `vnode_hascleanblks()`.
- Mount/vnode iteration: `vnode_iterate_setup()`, `vnode_umount_preflight()`, `vnode_iterate_prepare()`, `vnode_iterate_reloadq()`, `vnode_iterate_clear()`, `vnode_iterate()`, plus mount lock/ref helpers (`mount_lock*`, `mount_ref/drop`, `mount_iterref/drop/drain/reset`, `mount_refdrain()`).
- Root and mount lifecycle: `vfs_busy()`, `vfs_unbusy()`, `vfs_rootmountalloc()`, `vfs_mountroot()`, `vfs_switch_root()`, `vfs_mount_recovery()`, `vfs_unmountall()`, shutdown progress timestamp helpers.
- Mount lookup/list APIs: `vfs_getvfs()`, `vfs_getvfs_with_vfsops()`, `vfs_getvfs_by_mntonname()`, `vfs_getnewfsid()`, `vfs_iterate()`, `mount_list_add/remove()`, `mount_lookupby_volfsid()`, `mount_list_lookupby_fsid()`.
- Device vnode support: `bdevvp()`, `checkalias()`, `get_vp_from_dev()`, `check_mountedon()`, `vnode_cmp_chrtoblk()`, `vcount()`, `vfs_mountedon()`, `vfs_setmounting()`, `vfs_setmountedon()`, `vfs_clearmounting()`.
- Vnode lifecycle: `vget_internal()`, `vnode_ref*()`, `vnode_rele*()`, `vflush()`, `vclean()`, `vn_revoke()`, `vnode_recycle()`, `vnode_reload()`, `vnode_reclaim_internal()`, `new_vnode()`, `vnode_get*()`, `vnode_put*()`, `vnode_hold/drop*()`, `vnode_suspend/resume()`, `vnode_drain()`, `vnode_getiocount()`.
- Path/name helpers: `vn_getpath*()`, `vn_getcdhash()`, package extension table APIs (`set_package_extensions_table()`, `is_package_name()`, `vn_path_package_check()`), `vn_searchfs_inappropriate_name()`.
- VFS control/event APIs: `vfs_sysctl_node`, `sysctl_vfs_vfslist()`, `sysctl_vfs_ctlbyfsid()`, `vfs_event_init()`, `vfs_event_signal()`, EVFILT_FS filter callbacks, `vfs_update_vfsstat()`, `sysctl_vfs_noremotehang()`.
- Public vnode convenience APIs: `vnode_lookupat()`, `vnode_lookup()`, `vnode_open()`, `vnode_close()`, `vnode_mtime()`, `vnode_flags()`, `vnode_size()`, `vnode_setsize()`, dirty-bit helpers.
- Creation/auth entry points: `vn_create()`, `vnode_create_ext()`, `vnode_create()`, `vnode_create_empty()`, `vnode_initialize()`, `vnode_addfsref()`, `vnode_removefsref()`, `vnode_link_lock/unlock()`, `vnode_authorize_init()`, `vnode_authorize()`, `vn_authorize_unlink/open/create/rename/mkdir/rmdir()`, `vnode_attr_authorize_dir_clone()`.

## Control Flow

`vntblinit()` initializes all vnode and mount queues, configures reclaim/deallocation policy from boot tunables, optionally enables SMR freeing for the vnode zone, and starts two permanent worker threads: `async_work_continue()` and `vn_laundry_continue()`. Those threads consume async-work/free/rage queues and drive deferred reclaim through `process_vp()`.

Mount iteration moves `mnt_vnodelist` into `mnt_workerqueue` under mount locks, returns each vnode to the main list as it is examined, and tracks newly inserted vnodes in `mnt_newvnodes`. `vnode_iterate()` obtains an iocount with `vget_internal()` before invoking a caller callback, while `vflush()` uses the same queue mechanics to reclaim or forcibly close vnodes during unmount.

Root mounting allocates a provisional root mount for each candidate filesystem type, calls either `vfc_mountroot` or `VFS_MOUNT`, then publishes the mount, initializes I/O attributes, probes root capabilities, starts the filesystem, and optionally labels root under MACF. Failure unwinds via `vfs_rootmountfailed()`.

`vfs_switch_root()` performs a multi-step destructive root pivot: validate incoming root, find destination covered vnodes, collect preserved mounts (`/dev`, Preboot, Recovery, VM, Update, iSCPreboot, Hardware, xarts, FactoryLogs, Diags), take transferred usecounts, rewrite mount coverage and `rootvnode`, purge name caches, optionally reorder `mountlist`, and fix mount names/backing-root flags across all mounts.

Vnode creation flows through `new_vnode()` and `vnode_create_internal()`. `new_vnode()` either allocates a fresh vnode, reuses a dead/free/rage vnode, forces allocation in dependency/deadlock cases, or waits/retries under vnode pressure. `vnode_create_internal()` initializes type, ops, UBC state, trigger/device/FIFO metadata, mount/name-cache membership, rapid-aging flags, secluded-memory eligibility, and special alias substitution for block/char devices.

Reclaim flows converge on `vnode_reclaim_internal()`: mark terminating, clear union wait, optionally revoke ttys, drain outstanding iocounts, revoke leases when enabled, call `vgone()`/`vclean()` for non-`VBAD` vnodes, bump `v_id` under the vnode list lock, verify UBC/name/parent/output cleanup, reset knotes, wake terminators, and put non-reuse vnodes back on an eligible list.

Authorization begins with higher-level operation-specific checks (`vn_authorize_*`) and funnels through `vnode_authorize()` into the registered kauth callback. This chunk covers cache lookup for previously authorized rights, POSIX mode checks, ACL evaluation, delete semantics, immutable flag checks, opaque filesystem delegation, and superuser handling. The main callback implementation continues in the next chunk.

## State and Invariants

- Vnode lifetime is split across holdcount, iocount, usecount, kusecount, writecount, list membership, mount references, and named references (`VNAMED_*`). Many panics enforce counter balance and impossible list states.
- `v_id` is the generation guard for stale references; reclaim increments it while holding `vnode_list_lock` so `vnode_getwithvid()` can reject stale cache/hash references.
- `VL_TERMINATE`, `VL_DRAIN`, `VL_DEAD`, `VL_MARKTERM`, `VL_NEEDINACTIVE`, and `VL_SUSPENDED` drive the vnode state machine. Callers may block, fail, or bypass drains depending on flags such as `VNODE_DRAINO`, `VNODE_ALWAYS`, `VNODE_NOBLOCK`, and `VNODE_NODEAD`.
- Freeable vnode policy is controlled by `vn_dealloc_level`, `numvnodes_min/max`, `reusablevnodes_max`, dead vnode thresholds, and `VCANDEALLOC`; SMR freeing temporarily blocks `vnode_hold_smr()` using `VNODE_HOLD_NO_SMR`.
- Mount lifetime uses both `mnt_count` and `mnt_iterref`; unmount drain sets negative iterref state and mount busy uses shared/exclusive `mnt_rwlock`.
- Device alias state lives in `specinfo`, `speclisth`, `SI_ALIASED`, `SI_MOUNTING`, and `SI_MOUNTEDON`; alias transitions rely on SPECHASH locking plus vnode holds/iocounts outside the hash lock.
- Authorization caches successful rights on vnodes, with named streams sometimes caching on the parent data fork for local-authorization filesystems.

## Dependencies

This code depends heavily on XNU VFS and vnode internals (`mount_internal.h`, `vnode_internal.h`, namei, buf, UBC, VM memory objects, kauth, MACF, kqueue, sysctl, disk ioctls, specfs, fifofs, NFS). It calls filesystem VNOP/VFS methods including `VFS_MOUNT`, `VFS_START`, `VFS_ROOT`, `VFS_GETATTR`, `VNOP_CREATE`, `VNOP_MKNOD`, `VNOP_OPEN`, `VNOP_CLOSE`, `VNOP_FSYNC`, `VNOP_RECLAIM`, `VNOP_INACTIVE`, `VNOP_ACCESS`, `VNOP_IOCTL`, and compound operations. It also uses external helpers such as `namei()`, `vn_open()`, `vn_close()`, `build_path_with_parent()`, `cache_enter_create()`, `cache_purgevfs()`, `ubc_*`, `memory_object_*`, `kauth_acl_*`, `mac_vnode_*`, `dounmount()`, `safedounmount()`, and `kernel_mount()`.

## Risks and Edge Cases

- Lock ordering is critical: mount iterate mutex before mount lock, vnode lock versus vnode list lock, SPECHASH lock dropped before vnode iocount acquisition, and root switch holding `rootvnode_rw_lock` while rewriting mount topology.
- Forced unmount/reclaim paths can block indefinitely on leaked iocounts unless `bootarg_no_vnode_drain` enables timeout behavior; shutdown has a special iocount reset escape when no output is pending.
- `vnode_create_internal()` notes a real race for reused `bdevvp` alias vnodes where unlocked flag manipulation can lose `VTHROTTLED`; the code compensates with an unconditional wakeup and reasserts selected flags under lock.
- `vfs_switch_root()` intentionally reaches a point of no return after validation; failures after destructive mount rewrites would be hard to recover.
- Sysctl compatibility code explicitly blocks unsafe old-style filesystem selectors because some filesystems treat user pointers as `struct sysctl_req` and may call through arbitrary function pointers.
- Authorization correctness depends on subtle ACL/POSIX precedence, sticky bit handling, immutable flag exceptions, owner/group membership uncertainty, and rights-cache invalidation by setattr/xattr paths outside this chunk.
- `vn_path_package_check()` temporarily writes NUL terminators into the supplied path buffer while scanning components, so callers must pass mutable path storage.
- Vnode pressure handling can force allocation, trigger jetsam on configured platforms, or panic when no recovery path exists.

## Cross-Chunk References

- `vnode_authattr_new_internal()` is declared and called by `vn_attribute_prepare()` but its implementation is after this chunk.
- `vnode_authorize_callback_int()` begins at the chunk boundary and continues after line 10231; this chunk does not include the full action-to-rights mapping, attribute fetches, final cache decisions, or error propagation.
- Trigger resolver functions are declared and partially referenced during create/reclaim (`vnode_resolver_create()`, `vnode_resolver_detach()`), but their implementations are later.
- Lease cleanup is referenced under `CONFIG_FILE_LEASES` (`vnode_revokelease()`), but lease allocation/breaking logic is in a later chunk.
- Later helpers referenced here include union-wait functions, filesystem type-name setters/getters, AppleDouble orphan cleanup, panic vnode tracing, path tracing, and read-ahead advice.

## Research Notes

The assigned line range was read completely. No final per-file report was created for this chunked file.

### Chunk 2: lines 10232-13491

# Chunk Research: sources/os/darwin/xnu/bsd/vfs/vfs_subr.c lines 10232-13491

## Scope

This chunk covers the tail of vnode authorization, vnode attribute validation for create/setattr, assorted mount/vnode state helpers, orphaned AppleDouble cleanup during `rmdir`, panic/debug vnode tracing support, trigger vnode resolver plumbing, optional file lease management, and two small vnode utility APIs.

## APIs and Entry Points

- `vnode_authorize_callback_int()` continues from the previous chunk and completes local KAUTH authorization against vnode and optional parent attributes.
- `vnode_attr_authorize_init()` initializes the `vnode_attr` fields required by `vnode_attr_authorize()`.
- `vnode_attr_authorize()` authorizes already-fetched vnode attributes, including mount read-only/noexec checks and local security completeness checks.
- `vnode_authattr_new()` / `vnode_authattr_new_internal()` default and validate attributes for new objects.
- `vnode_authattr()` validates requested `VNOP_SETATTR` attributes and returns the KAUTH rights needed to apply them.
- `vfs_setlocklocal()`, `vfs_setcompoundopen()`, `vnode_setswapmount()`, `vfs_setfskit()`, `vfs_getextflags()`, `vfs_getfstypename()`, and `vfs_setfstypename()` mutate or expose mount-level feature flags/name state.
- `vnode_getswappin_avail()` reads mount swap-pin availability under the mount lock.
- `vn_setunionwait()`, `vn_checkunionwait()`, and `vn_clearunionwait()` implement a vnode flag wait/wakeup protocol around `VISUNION`.
- `rmdir_remove_orphaned_appleDouble()` validates and removes only orphaned `._*` entries from an otherwise empty directory before retrying `rmdir`.
- `lock_vnode_and_post()` posts vnode knotes after taking the vnode lock when listeners exist.
- `panic_print_vnodes()` is either a no-op or a panic-path vnode list dumper under `PANIC_PRINTS_VNODES`.
- `vfs_resolver_result()` and, under `CONFIG_TRIGGERS`, `vfs_resolver_status()`, `vfs_resolver_sequence()`, and `vfs_resolver_auxiliary()` pack/unpack trigger resolver status.
- Trigger APIs include `vnode_trigger_update()`, `vnode_trigger_rearm()`, `vnode_trigger_resolve()`, `vfs_nested_trigger_unmounts()`, and `vfs_addtrigger()`.
- `kdebug_vnode()`, `vnode_should_flush_after_write()`, and the `vfs.generic.trace_paths` sysctl support tracing/cache diagnostics.
- Under `CONFIG_FILE_LEASES`, public lease APIs include `vnode_setlease()`, `vnode_getlease()`, `vnode_breaklease()`, `vnode_breakdirlease()`, and `vnode_revokelease()`.
- `vnode_rdadvise()` sends `F_RDADVISE` to a vnode.
- `vnode_hasmultipath()` determines whether a vnode has multiple paths by cached flags or link-count attributes.

## Key Control Flow

Authorization:
1. `vnode_authorize_callback_int()` strips control bits from `action`, optionally reuses cached parent `DELETE_CHILD`, rejects writes on read-only mounts and execute on noexec mounts, and delegates opaque authorization when `MNTK_AUTH_OPAQUE` applies.
2. Namedstream data rights are translated into extended-attribute rights; if possible, authorization switches to the stream parent vnode after `vget_internal()`.
3. Root is allowed early for non-execute/non-write requests; otherwise the function fetches mode/flags and, for non-root, uid/gid/ACLs for the vnode and optional parent.
4. The actual security decision goes through `vnode_attr_authorize_internal()` from the previous chunk; ACLs are freed, parent references dropped, deny results are returned through `errorp`, and successful directory search may cache `KAUTH_VNODE_SEARCHBYANYONE`.

Attribute create/setattr:
1. `vnode_attr_authorize_init()` declares required fields and rejects delete authorization without parent attributes.
2. `vnode_attr_authorize()` validates mount policy and attribute completeness, temporarily maps uid/gid through `vnode_attr_handle_uid_and_gid()`, calls `vnode_attr_authorize_internal()`, restores original uid/gid, and maps `EPERM` to `EACCES`.
3. `vnode_authattr_new_internal()` rejects extended security fields on filesystems without extended security, defaults uid/gid/mode/create time, inherits `UF_DATAVAULT` and `SF_RESTRICTED`, validates flag masks, and enforces non-root ownership/group/UUID/setuid/setgid constraints.
4. `vnode_authattr()` rejects read-only attributes, fetches only old attributes needed for requested changes, validates data-size changes, timestamps, mode bits, flags, uid/gid/UUID changes, ACL changes, and encoding changes, then writes the required KAUTH action mask to `*actionp`.

AppleDouble cleanup:
1. `rmdir_remove_orphaned_appleDouble()` suspends the directory vnode, sets `UT_NSPACE_NODATALESSFAULTS`, opens the directory, and scans it with `VNOP_READDIR()`.
2. The first pass allows only `.`/`..` and regular-looking names beginning with `._`, rejecting nested `._._` names and any other entry with `ENOTEMPTY`.
3. The second pass calls `unlink1()` for each remaining non-dot entry while suppressing namespace events and audit path generation.
4. HFS and NFS get explicit EOF workarounds; all exits close/free/restore thread flags and resume the vnode.

Trigger vnodes:
1. Resolver results encode sequence, auxiliary errno, and status into a `uint64_t`.
2. `vnode_resolver_create()` allocates resolver state, copies callbacks/data/flags from trigger parameters, attaches state to the vnode, optionally takes an external forced reference, and increments `mnt_numtriggers`.
3. `vnode_trigger_resolve()` skips already-resolved or covered vnodes, runs MACF checks for non-kernel-resolved triggers, calls the resolver callback, updates state only for newer sequence numbers, and returns resolver auxiliary errno on `RESOLVER_ERROR`.
4. `vnode_trigger_unresolve()` marks `VNT_VFS_UNMOUNTED`, invokes the unresolver, updates sequence/state, clears the unmounting flag, and returns auxiliary errors.
5. `vfs_nested_trigger_unmounts()` iterates mounts tail-first, defers unresolve work outside the active mount iterator reference, and uses vnode ids/holds to avoid stale vnode reuse.
6. `vfs_addtrigger()` roots lookup inside a mount with `NOCROSSMOUNT`, resolves a relative path, converts `vnode_trigger_info` to `vnode_trigger_param`, and attaches an external resolver.

File leases:
1. `vnode_setlease()` gates all lease set/release operations on the private file-lease entitlement, then dispatches to acquire or release paths.
2. `acquire_file_lease()` validates expected open counts, checks open/write/mmap conflicts, coalesces leases owned by the same pid or fileglob, and rejects conflicting third-party leases.
3. `vnode_breaklease()` determines read-vs-write breaker intent from open flags, skips certain read/dataless cases, marks conflicting leases for downgrade or release, posts knote events, and either returns `EWOULDBLOCK` for nonblocking callers or sleeps until holders respond or time out.
4. `handle_lease_break_timedout()` forcibly downgrades or releases leases whose timers exceed `lease_break_timeout`, then wakes waiters.
5. `vnode_breakdirlease()` best-effort locates a parent by name cache or filesystem parent id before breaking directory leases.
6. `vnode_revokelease()` removes all leases during vnode reclaim and wakes any blocked breakers.

## State and Dependencies

- Authorization state flows through `_vnode_authorize_context`, `vnode_attr`, `kauth_action_t`, cached vnode authorization rights, mount flags (`MNT_RDONLY`, `MNT_NOEXEC`, `MNT_IGNORE_OWNERSHIP`, `MNTK_AUTH_OPAQUE`), and vnode flags/types.
- Attribute validation mutates caller-supplied `vnode_attr` values: defaulted uid/gid/mode/create time, inherited `UF_DATAVAULT`/`SF_RESTRICTED`, stripped `SF_SYNTHETIC`, and possibly masked setuid/setgid bits.
- Mount helper state includes `mnt_kern_flag`, `mnt_compound_ops`, `mnt_ioflags`, `mnt_max_swappin_available`, `fstypename_override`, and external mount flags returned via `vfs_getextflags()`.
- Union wait state uses `VISUNION` in `v_flag`, `msleep()`, and `wakeup()` on `&vp->v_flag`.
- AppleDouble cleanup depends on `vnode_suspend()/vnode_resume()`, `VNOP_OPEN/CLOSE/READDIR`, `uio_*`, `unlink1()`, current uthread flags, and filesystem tags `VT_HFS`/`VT_NFS`.
- Panic/debug paths depend on `mountlist`, per-mount vnode lists, `ml_validate_nofault()`, `paniclog_append_noflush()`, `OSBacktrace()`, and bootargs controlling iocount tracing.
- Trigger state depends on `vp->v_resolve`, `struct vnode_resolve`, per-resolver mutexes, callback function pointers, sequence ordering, `mnt_numtriggers`, name cache locking, mount iteration, vnode holds/refs/iocounts, and optional MACF checks.
- File leases live on `vp->v_leases` and use vnode lock protection, `v_usecount`, `v_writecount`, writable UBC mapping state, fileglob identity, pid ownership, knote events, `mach_absolute_time()`, `msleep()`, and entitlement checks through IOKit.
- `vnode_hasmultipath()` depends on `MNTK_DIR_HARDLINKS`, `VE_NOT_HARDLINK`, `vnode_link_lock()`, and `va_nlink`/`va_dirlinkcount`.

## Risks and Edge Cases

- The chunk begins mid-function; `vnode_authorize_callback_int()` depends on prior initialization and on `vnode_attr_authorize_internal()` immediately preceding this chunk.
- `found_deny` is initialized false in `vnode_authorize_callback_int()` but set conservatively for root inside `vnode_attr_authorize_internal()`; caching `SEARCHBYANYONE` depends on this cross-function contract.
- Namedstream authorization changes `vp` to the parent after taking an iocount; all debug/error reporting and cache decisions after that point refer to the parent vnode, not the original stream vnode.
- `vnode_attr_authorize()` panics if required security attributes are active but unsupported; callers must follow `vnode_attr_authorize_init()`-style field preparation.
- `vnode_authattr_new_internal()` applies inherited restricted/datavault flags in `out:` even after earlier errors, so callers can observe modified attributes on failure.
- `vnode_authattr()` may mutate requested attributes by stripping `SF_SYNTHETIC` and masking setuid/setgid bits; it is not a pure validator.
- AppleDouble scanning trusts `d_reclen` while iterating the buffer returned by `VNOP_READDIR()`; correctness depends on filesystem-provided directory entries being well formed.
- The AppleDouble routine deletes all non-dot entries on the second pass after the first pass validates names; concurrent mutations are mitigated by vnode suspension but filesystem behavior still matters, especially for HFS/NFS EOF quirks.
- Panic vnode dumping intentionally avoids locks and allocations, so paths are best-effort and may race with corrupted lists; `ml_validate_nofault()` limits panic-path damage.
- Trigger callbacks run outside the resolver lock and comments explicitly warn about deadlock if callbacks access the trigger vnode.
- Trigger sequence numbers silently ignore stale callback results; resolver implementations must monotonically increase sequences for state updates to take effect.
- `vfs_nested_trigger_unmounts()` is best-effort, performs no retries, and stops early on unresolve errors.
- File lease ownership treats same pid or same fileglob as "ours", which can coalesce independent descriptors in the same process.
- Lease breaking sleeps with the vnode lock and depends on knote delivery to lease holders; timeout handling forcibly downgrades/releases leases.
- `wait_for_lease_break()` contains a suspicious condition `if (error == 0 || error != EWOULDBLOCK)`, equivalent to `error != EWOULDBLOCK`; this treats unexpected sleep errors like normal wakeups.
- `vnode_breaklease()` calls `is_dataless_file()` while holding the vnode lock; that helper performs `vnode_getattr()`, so filesystem locking expectations are important.
- `vnode_breakdirlease()` is intentionally best-effort when locating parents; failure to locate a parent means no lease break.
- `vnode_hasmultipath()` caches negative results with `VE_NOT_HARDLINK`, so later link-count changes must clear or bypass that cache elsewhere.

## Cross-Chunk References

- Lines before this chunk define the fast authorization cache path and `vnode_attr_authorize_internal()`, which this chunk calls at lines 10395 and 10548.
- Earlier code calls `vnode_authattr_new_internal()` through create-preparation paths around line 8179, so this chunk supplies the new-object defaulting and validation backend.
- Earlier authorization wrappers call `vnode_authorize()` for delete, rename, extended attributes, and directory operations; this chunk contains the slow callback completion that those wrappers ultimately depend on.
- Trigger vnode fields and lifecycle cleanup are only partially visible here; vnode reclaim/detach callers outside this chunk must call `vnode_resolver_detach()` after draining.
- `rmdir_remove_orphaned_appleDouble()` is declared near the top of the file and implemented here; its caller is outside this range and is expected to retry `VNOP_RMDIR()` when cleanup succeeds.
- File lease structures and flags are configured by headers/outside definitions; this chunk owns the main vnode-side state machine, while open/close/reclaim callers outside the chunk decide when to set, break, release, or revoke leases.
