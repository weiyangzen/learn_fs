# File Research: sources/os/linux/linux/fs/resctrl/rdtgroup.c

## Purpose
Implements the resctrl filesystem: mount lifecycle, kernfs tree construction, resource group creation/removal/rename, CLOSID allocation, task/CPU assignment, mode changes, info files, monitor-data directories, CPU/domain hotplug handling, and top-level initialization/exit.

## Main Responsibilities
- Register and manage the `resctrl` filesystem.
- Build the root group, info directories, monitor directories, and per-group files.
- Track all rdtgroups and the global schema list.
- Allocate/free CLOSIDs for control groups.
- Move tasks and CPUs between control and monitor groups.
- Implement group modes: shareable, exclusive, pseudo-locksetup, pseudo-locked.
- Initialize default CAT/MBA allocations for new groups.
- Handle mount options: `cdp`, `cdpl2`, `mba_MBps`, and `debug`.
- Create/remove monitor event files for each domain and group.
- Handle CPU and domain online/offline callbacks.
- Coordinate teardown on unmount or fatal architecture exit.

## Key Global State
- `rdtgroup_mutex`: protects rdtgroup filesystem state.
- `rdt_root`: kernfs root.
- `rdtgroup_default`: root/default control group.
- `rdt_all_groups`: list of all control groups.
- `resctrl_schema_all`: active allocation schemas.
- `mon_data_kn_priv_list`: shared `struct mon_data` instances for monitor files.
- `resctrl_mounted`: single-mount guard.
- `kn_info`, `kn_mongrp`, `kn_mondata`: key root kernfs nodes.
- `max_name_width`: schemata display formatting width.
- `last_cmd_status`: last user-command status buffer.
- `debugfs_resctrl`: debugfs root for resctrl pseudo-lock measurement files.
- `mba_mbps_default_event`: default MBM event used by MBA software controller.

## Important Control Flow
- Mount:
  - `rdt_get_tree()` enforces single mount, sets up RMID LRU, root kernfs tree, mount options, schema list, CLOSID bitmap, base files, info files, monitor directories, pseudo-lock device support, and delayed MBM overflow workers.
  - Enables architecture allocation/monitoring after kernfs tree creation succeeds.
- Unmount:
  - `rdt_kill_sb()` disables mount context, resets architecture controls, tears down filesystem state, disables allocation/monitoring, clears `resctrl_mounted`, and kills kernfs superblock.
- Files:
  - `res_common_files[]` is the central file table. It maps names, permissions, flags, show callbacks, and write callbacks for all info/base/control/monitor/debug files.
  - `rdtgroup_add_files()` filters this table by `RFTYPE_*` flags.
- CLOSIDs:
  - `closid_init()` computes the minimum CLOSID count across enabled schemas and reserves CLOSID 0 for the default group.
  - `closid_alloc()` optionally chooses the cleanest CLOSID when RMIDs depend on CLOSID.
  - `closid_free()`, `closid_allocated()`, and `closid_alloc_fixed()` manage the bitmap.
- CPU assignment:
  - `rdtgroup_cpus_write()` parses CPU masks/lists, rejects offline CPUs and pseudo-lock groups, then dispatches to control or monitor group handling.
  - Control groups return dropped CPUs to default and clear child monitor masks when parent membership changes.
  - Monitor groups can only use CPUs that belong to their parent control group.
- Task assignment:
  - `rdtgroup_tasks_write()` parses comma-separated PIDs.
  - Permission checks require root or task owner/saved owner.
  - Monitor groups cannot move tasks across control-group CLOSID boundaries.
  - Current tasks get immediate architecture state updates.
- Modes:
  - `rdtgroup_mode_write()` supports `shareable`, `exclusive`, and `pseudo-locksetup`; `pseudo-locked` is reached only after pseudo-lock creation.
  - Exclusive mode verifies no CBM overlap with other allocations.
  - Pseudo-locksetup delegates entry/exit to `pseudo_lock.c`.
- Info and monitor tree:
  - `rdtgroup_create_info_dir()` creates `info`, allocation resource dirs, and monitor resource dirs.
  - `mkdir_mondata_all()` creates per-group `mon_data` and per-domain event files.
  - SNC L3 systems create sum directories plus `mon_sub_*` domain directories.
- Group creation/removal:
  - `rdtgroup_mkdir_ctrl_mon()` creates top-level control+monitor groups, allocates CLOSID/RMID, initializes allocations, and adds `mon_groups`.
  - `rdtgroup_mkdir_mon()` creates monitor-only child groups under `mon_groups`.
  - `rdtgroup_rmdir_ctrl()` and `rdtgroup_rmdir_mon()` move tasks/CPUs back, update per-CPU defaults/MSRs, unassign counters, free RMIDs/CLOSIDs, and remove kernfs nodes.
  - `rdtgroup_rename()` supports moving monitor groups between parents when they are not monitoring CPUs.
- Domain/CPU hotplug:
  - `resctrl_online_ctrl_domain()` allocates MBA-SC per-domain state.
  - `resctrl_online_mon_domain()` allocates L3 monitor state, starts delayed workers, and creates monitor-data directories if mounted.
  - `resctrl_offline_mon_domain()` removes domain monitor directories, cancels delayed work, force-cleans busy RMIDs if needed, and frees domain monitor state.
  - `resctrl_online_cpu()` adds CPUs to default group; `resctrl_offline_cpu()` removes CPUs from groups and reschedules delayed work away from the offline CPU.

## Dependencies and Integration
- `ctrlmondata.c` supplies schemata, monitor-data display, MBA event, and I/O allocation file handlers referenced in `res_common_files[]`.
- `monitor.c` supplies RMID lifecycle, MBM assignment, monitor init/exit, and delayed work handlers.
- `pseudo_lock.c` supplies pseudo-lock mode entry/exit/create/remove and device lifecycle.
- Relies on architecture hooks for CDP, CLOSID/RMID scheduling state, control MSR updates, monitor capability, domain resources, and enable/disable operations.

## Concurrency and Lifetime
- Most operations use `rdtgroup_kn_lock_live()`/`rdtgroup_kn_unlock()` to combine kernfs active-reference handling, CPU hotplug protection, and `rdtgroup_mutex`.
- `waitcount` and `RDT_DELETED` protect rdtgroup memory while files/devices are still open.
- `rdtgroup_kn_get()` breaks kernfs active protection before taking global locks; `rdtgroup_kn_put()` restores it and frees deleted groups when references drain.

## Error Handling
- User-facing failures are usually recorded in `last_cmd_status`.
- Mount has structured unwind labels for pseudo-lock, monitor-data, mon_groups, info, CLOSID, schema, mount context, and root teardown.
- Group creation carefully unwinds kernfs nodes, RMIDs, CLOSIDs, counters, and list membership.
- Teardown forcibly moves all tasks and CPUs back to default state.

## Research Notes
This is the central orchestrator for resctrl. Its correctness depends on consistent lock ordering, kernfs lifetime handling, architecture-hook behavior, and strict separation between control groups and monitor groups. It is also where feature visibility is decided, so adding a new resctrl file usually requires changes to `res_common_files[]` and feature flag initialization.
