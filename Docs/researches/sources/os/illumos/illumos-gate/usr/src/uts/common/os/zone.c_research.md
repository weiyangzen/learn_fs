# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/zone.c

Core kernel implementation of illumos zones. It owns zone lifecycle state, global zone initialization, zone-specific data callbacks, resource controls, kstats, zone lookup and reference accounting, zone system-call dispatch, `zsched` creation, process zone entry, shutdown/destroy, ZFS dataset visibility, datalink assignment, and zone network metadata.

Key elements:
- The opening design comment documents the zone state machine from `ZONE_IS_UNINITIALIZED` through `ZONE_IS_FREE`, lock ordering, visible syscall operations, and zone-specific data semantics.
- Global state includes `zone0`/`global_zone`, active and deathrow zone lists, hash tables by id/name/label, zone ID space, ZSD key list, resource-control handles, and zone event channel.
- Mount synchronization uses `block_mounts()`, `resume_mounts()`, `mount_in_progress()`, and `mount_completed()` to prevent racing VFS mounts with zone state transitions.
- Zone Specific Data support includes `zone_key_create()`, `zone_key_delete()`, `zone_setspecific()`, `zone_getspecific()`, `zone_zsd_configure()`, `zone_zsd_callbacks()`, and apply/wait helpers. Callbacks are marked under locks, then executed after dropping locks to avoid callback-induced lock inversions.
- Resource-control callbacks implement zone usage/test/set logic for CPU shares/cap, max LWPs, max processes, System V IPC IDs/memory, locked memory, swap reservation, and lofi limits.
- Kstat helpers create and update per-zone `lockedmem`, `swapresv`, `nprocs`, `memory_cap`, and `zone_misc` kstats.
- `zone_zsd_init()` performs very early setup and partially initializes `zone0`; `zone_init()` registers rctls, finalizes global-zone state, initializes label/kstat/hash structures, and binds the zone sysevent channel.
- `zone_free()` tears down all zone-owned resources: CPU caps, ZSD entries, dataset list, datalink/network nvlists, CPU accounting arrays, vnodes, labels, strings, privileges, rctls, boot/init data, doors, locks, and the zone ID.
- `zone_status_set()` publishes zone state-change sysevents and wakes waiters; wait helpers provide blocking, signal-aware, timed, and CPR-safe state waits.
- Reference management distinguishes general references, credential references, task references, and tracked subsystem crumbs through `zone_hold()`, `zone_rele()`, `zone_hold_ref()`, `zone_rele_ref()`, `zone_cred_hold()`, `zone_cred_rele()`, `zone_task_hold()`, and `zone_task_rele()`.
- Lookup APIs find held zones by id, name, label, root path, or any zone path while filtering by externally visible state.
- Load and CPU visibility helpers update per-zone load averages and pool/processor-set visibility.
- `zone_set_root()`, `zone_set_name()`, `zone_set_privset()`, `zone_set_brand()`, `zone_set_secflags()`, `zone_set_initname()`, `zone_set_bootargs()`, `zone_set_fs_allowed()`, `zone_set_sched_class()`, and `zone_set_phys_mcap()` validate and store zone attributes.
- `zsched()` builds the per-zone kernel parent process, moves it into the new zone, creates project/task/rctl context, chroots it to the zone root, marks the zone initialized/ready, launches init after `ZONE_IS_BOOTING`, then waits for `ZONE_IS_DYING`.
- `zone_create()` allocates a zone ID, validates root/name/privileges/rctls/ZFS datasets/labels, serializes against mounts, installs a restricted `zone_kcred`, inserts the zone into hashes/lists, starts `zsched`, creates kstats, waits until ready, and returns the new zone ID.
- `zone_boot()` transitions a ready zone to booting and waits for running or boot failure.
- `zone_shutdown()` blocks mounts, transitions to shutting down/empty/down as appropriate, kills zone processes, rebinds pool visibility, runs ZSD shutdown callbacks, and waits for zone kernel threads to drain.
- `zone_destroy()` requires the zone to be down, tells `zsched` to exit, runs destroy callbacks, waits for remaining references with periodic reference-count logging, removes hashes/lists/kstats/brand state, and drops the final hold.
- `zone_getattr()` and `zone_setattr()` implement the user-visible zone attribute API, including root/name/status/flags/privileges/uniqid/pool/label/init/brand/bootargs/memory cap/scheduler/hostid/filesystem/security/network attributes plus brand-specific extensions.
- `zone_enter()` injects the current global-zone process into a ready/running non-global zone. It stops sibling LWPs, validates files/mappings/contracts/privileges, binds pools, transfers task/project/process/LWP/memory/swap/crypto accounting, resets contracts/session/scheduler state, chroots, restricts credentials and privileges, adjusts UID counts, and resets core defaults.
- `zone()` is the syscall dispatcher for create, boot, destroy, getattr, setattr, enter, list, shutdown, lookup, version, and datalink operations, including 32-bit `zone_def` translation.
- `zone_kadmin()` handles in-zone `uadmin()` shutdown/reboot by marking the zone shutting down, killing zone processes, and starting a global-zone kernel thread to call `zoneadmd` through a door.
- `zone_shutdown_global()` marks the global zone and running zones as shutting down during system shutdown.
- `zone_dataset_visible()` checks delegated ZFS datasets and mounted ZFS filesystems for read/write visibility from the current zone.
- Datalink support maintains per-zone `zone_dl_t` entries through add/remove/check/list/walk APIs and ensures a link ID belongs to only one zone.
- Network metadata support maps address/default-router entries into per-datalink nvlists through `zone_set_network()` and `zone_get_network()`.

Dependencies:
- Deeply integrated with process, task, project, credential, privilege, contract, session, signal, scheduler, pool, processor-set, vnode/VFS, VM segment, resource-control, kstat, brand, MAC/datalink, ZFS visibility, Trusted Extensions label, sysevent, door, and uadmin subsystems.
- Uses `mod_hash` for zone lookup, `id_space` for zone IDs, `list_t` for active/deathrow/ZSD/dataset/datalink lists, `nvlist` for rctl/network payloads, and many kernel locks/CVs.
- Depends on external policy gates such as `secpolicy_zone_config()`, `secpolicy_pool()`, and `secpolicy_zone_admin()`.

Research notes:
- State transitions are intentionally monotonic; callers wait for "at least this state" rather than exact reversibility.
- The code separates visible lifecycle removal from memory freeing so credential references can survive a destroyed zone; dead zones may remain on `zone_deathrow`.
- Mount synchronization is explicitly per-zone but biased toward the current operation, and comments acknowledge possible shutdown starvation during rapid mount activity.
- Zone ID allocation avoids reusing IDs whose corresponding netstack ID is still referenced, warning and retrying instead.
- `zone_destroy()` logs subsystem reference counts after a timeout to aid leaked-reference debugging.
- `zone_enter()` has a large "cannot fail from now on" point after accounting and zone membership are transferred; rollback is only attempted before that point.
- A notable local quirk appears in `zone_create()`: while initializing a newly allocated zone, it assigns `zone0.zone_lockedmem_kstat` and `zone0.zone_swapresv_kstat` to `NULL`, which looks inconsistent with the surrounding per-zone initialization.
