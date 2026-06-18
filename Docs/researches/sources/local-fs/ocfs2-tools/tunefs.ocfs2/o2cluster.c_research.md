# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/o2cluster.c

## Purpose
Implements `o2cluster`, a utility to list or update the cluster stack descriptor stamped on an OCFS2 filesystem.

## Main Behavior
- Supports tasks:
  - `--show-running`: print active cluster stack.
  - `--show-ondisk <device>`: print cluster stack stored on disk.
  - `--update[=<clusterstack>] <device>`: update on-disk cluster stack, using the running cluster if no argument is supplied.
- `parse_cluster_info()` accepts:
  - `default`
  - `<stack>,<cluster>,<hbmode>`
  - validates stack names, cluster names, and heartbeat modes.
- `fs_open()` opens the device rw with strict compatibility checks and heartbeat-device allowance.
- `journal_check()` scans all journal system inodes and aborts if any journal is dirty.
- `do_update()`:
  - Opens the filesystem.
  - Refuses local/non-clustered filesystems.
  - Refuses dirty journals.
  - Reads current on-disk descriptor.
  - No-ops when requested descriptor already matches.
  - Prompts before changing descriptor.
  - Writes via `ocfs2_set_cluster_desc()`.
- `do_list_ondisk()` refuses local filesystems, then prints descriptor.
- `do_list_active()` initializes O2CB and prints the running descriptor.
- Installs signal handlers and initializes error tables/verbosity in `tool_init()`.

## Dependencies
- OCFS2 open, journal/system inode, bitops, mount/cluster descriptor APIs.
- O2CB cluster stack APIs.
- O2DLM/O2CB/OCFS2 error tables.
- `tools-internal` verbose/progress/interactive helpers.

## Safety Notes
The tool intentionally refuses updates if journals are dirty because it cannot distinguish an active mount from an unrecovered crash without joining the cluster. It still has a documented race between clean-journal check and another node mounting with the old cluster stack.
