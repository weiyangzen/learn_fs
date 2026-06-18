# File Research: sources/local-fs/gfs2-utils/gfs2/scripts/gfs2_lockcapture

Python diagnostic collector for GFS2 and DLM lock information. It discovers cluster identity, finds mounted GFS2 filesystems, collects DLM/GFS2 debugfs data over repeated runs, captures host/process/log diagnostics, archives the output, and cleans up.

Main data model:
- `ClusterNode`: cluster node name/id, cluster name, and mounted GFS2 filesystem label map.

Important helpers:
- Command helpers: `runCommand`, `runCommandOutput`
- File helpers: `writeToFile`, `mkdirs`, `copyFile`, `copyDirectory`, `backupOutputDirectory`, `archiveData`
- Runtime helpers: `mountFilesystem`, `removePIDFile`, `exitScript`
- Cluster discovery: `getClusterNode`, `getMountedGFS2Filesystems`, `getLabelMapForMountedFilesystems`
- DLM discovery: `parse_dlm_ls`, `getGroupToolDLMLockspaces`, `getDLMLockspaces`, `getVerifiedDLMLockspaceNames`
- Collection: `gatherHostData`, `gatherDiagnosticData`, `gatherOptionalDiagnosticData`, `gatherPidData`, `triggerSysRQEvents`, `gatherLogs`, `gatherDLMLockDumps`, `gatherGFS2LockDumps`
- CLI: `OptionParserExtended`, `ExtendOption`, `__getOptions`

Default paths:
- Debugfs: `/sys/kernel/debug`
- PID file: `/var/run/<script>.pid`
- Output root: `/tmp`
- Per-day output: `<output>/gfs2_lockcapture-YYYY-MM-DD`
- Archive: `<outputdir>-<hostname>.tar.bz2`

CLI supports debug/quiet/no-ask/info, process gathering disable, hidden optional diagnostics, output directory, run count, sleep interval, and selected GFS2 filesystem names.

Behavioral flow:
1. Create logger and PID file, preventing concurrent runs.
2. Discover cluster name/node via `cman_tool` or corosync tools.
3. Match mounted GFS2 filesystems by cluster-prefixed mount labels.
4. Optionally print filesystem info and exit.
5. Ask before process stack/sysrq collection unless disabled.
6. Prepare output directory, mounting debugfs if needed.
7. For each run, gather host info, DLM lock dumps, GFS2 lock dumps, process stacks or sysrq traces, logs, and diagnostics.
8. Sleep between runs.
9. Compress output and remove uncompressed directory if archive succeeds.

Research notes:
- The script is compatibility-oriented and uses old cluster tooling (`cman_tool`, `group_tool`) plus corosync alternatives.
- `ExtendOption.take_action` appears to append the whole comma string once per comma item instead of appending each split item, because it uses `value.strip()` instead of `v.strip()`.
- It may trigger sysrq `t`, so it is operationally invasive.
