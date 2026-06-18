# File Research: sources/os/linux/linux-stable/fs/resctrl/rdtgroup.c

Main resctrl filesystem implementation. It owns global group state, kernfs file layout, mount/unmount, group creation/removal, CPU/task assignment, schema creation, info files, monitor-data directories, and CPU/domain hotplug integration.

Key responsibilities:
- Defines `rdtgroup_mutex`, `rdtgroup_default`, `rdt_all_groups`, `resctrl_schema_all`, mount state, info/monitor kernfs nodes, `last_cmd_status`, and debugfs root.
- Implements CLOSID allocation using a global bitmap, with cleanest-CLOSID selection when RMID state depends on CLOSID.
- Implements `last_cmd_status` accumulation for user-visible write errors.
- Provides kernfs operation wrappers for common resctrl files and mon_data files.
- Handles `cpus`/`cpus_list` writes for control groups and monitor groups, moving CPUs between groups and updating architecture closid/rmid state.
- Handles `tasks` writes and task migration with permission checks, closid/rmid update ordering, and immediate update of current tasks via IPI when needed.
- Implements `/proc` resctrl display when enabled.
- Provides info-file readers for closids, RMIDs, monitor features, cache masks, bit usage, MBA properties, thread throttle mode, and threshold occupancy.
- Implements group modes and transitions between shareable, exclusive, pseudo-locksetup, and pseudo-locked, including CBM overlap tests.
- Implements MBM event configuration files and BMEC visibility.
- Defines `res_common_files[]`, the central table of resctrl files and callbacks.
- Builds the `info` tree and per-resource/monitor info directories based on resource capability flags.
- Parses mount options `cdp`, `cdpl2`, `mba_MBps`, and `debug`, then enables architecture context and builds schemas on mount.
- Sets up root, info, `mon_groups`, `mon_data`, pseudo-lock device class, and enables architecture allocation/monitoring in `rdt_get_tree()`.
- Tears down all groups and resets controls in `rdt_kill_sb()` and `resctrl_exit()`.

Group lifecycle:
- Control groups are created under root, receive a CLOSID, optional RMID, default CAT/MBA allocations, `mon_groups`, and mon_data.
- Monitor groups are created only under a parent `mon_groups` directory, share the parent CLOSID, receive their own RMID, and get mon_data.
- Removal moves tasks/CPUs back to parent/default groups, updates CPU defaults/MSRs, unassigns counters, frees RMID/CLOSID, removes kernfs nodes, and handles open references through `waitcount`/`RDT_DELETED`.
- Monitor groups can be renamed or reparented if they do not monitor CPUs.

Monitor-data layout:
- Creates `mon_data/mon_<resource>_<domain>` directories with one file per enabled event.
- For L3 SNC node scope, creates aggregate `mon_L3_<cacheid>` directories with subdomain directories.
- Reuses `struct mon_data` objects across identical event/domain/sum files.

Domain/CPU hotplug:
- Online control domains allocate MBA software-controller per-domain arrays when applicable.
- Online monitor domains allocate RMID busy bitmaps, MBM state arrays, assignable counter config, delayed work, and mon_data directories if mounted.
- Offline monitor domains remove mon_data directories, cancel work, force-free limbo RMIDs if needed, and destroy domain monitor state.
- CPU online adds the CPU to the default group; CPU offline removes it from current group/child masks and reschedules work off that CPU.

Notable invariants:
- resctrl can be mounted only once.
- Many operations require both `cpus_read_lock()` and `rdtgroup_mutex`.
- Schemata are generated after mount options because CDP changes visible resources and CLOSID counts.
- Default group always uses reserved CLOSID/RMID.
