# File Research: sources/local-fs/dlm/dlm_controld/action.c

## Purpose
Kernel-facing action layer for `dlm_controld`. It writes DLM sysfs/configfs controls, discovers cluster names and misc device minors, initializes configfs cluster options, manages configfs node/member directories, and detects abandoned kernel lockspaces.

## Main Behavior
- Detects Corosync cluster name through `cmap_get_string("totem.cluster_name")` and stores it in global `cluster_name`.
- `check_uncontrolled_lockspaces()` scans `/sys/kernel/dlm`; if lockspaces exist before daemon control is established, it logs them and kicks the local node from the cluster.
- Sysfs helpers write lockspace `control`, `event_done`, `id`, and `nodir` values under `/sys/kernel/dlm/<name>/`.
- Configfs member helpers manage `/sys/kernel/config/dlm/cluster/spaces/<lockspace>/nodes/<nodeid>`:
  - Create lockspace and node directories.
  - Remove old members no longer present.
  - Renew nodes by rmdir/mkdir when a node left and rejoined.
  - Write each node's `nodeid` and configured master `weight`.
  - Optionally write `release_recover` for a member before removal.
- Configfs communication helpers manage `/sys/kernel/config/dlm/cluster/comms/<nodeid>`:
  - Create node directories.
  - Write nodeid, padded sockaddr storage address, optional skb mark, and local flag.
  - Delete individual comm nodes or clear all comm nodes.
- `setup_configfs_options()` clears stale configfs state, recreates base cluster directory, writes selected cluster options, validates protocol selection (`tcp`/`sctp`; `detect` is rejected to TCP), configures SCTP receive buffers, enables recovery callbacks, and writes cluster name unless deprecated fscontrol mode is active.
- `setup_misc_devices()` parses `/proc/misc` for `dlm-control`, `dlm-monitor`, and `dlm_plock`, then waits for matching `/dev/misc/*` device nodes.

## Integration Points
- Calls cross-module helpers from `main.c`, `member.c`, and `config.c`: `do_write`, `kick_node_from_cluster`, `is_cluster_member`, `update_cluster`, and `get_weight`.
- Consumes daemon options from `dlm_options` through `opt`, `optu`, and `opts`.
- Provides kernel control primitives used by the CPG membership code in `cpg.c`.

## Risks and Notes
- Many operations require mounted configfs, loaded DLM kernel module, and correct permissions.
- String formatting uses fixed-size buffers with `snprintf` in most places; paths longer than `PATH_MAX` are truncated but not explicitly detected.
- `add_configfs_node()` treats failure to open the optional `mark` file as non-fatal because older kernels may not support it.
- Cleaning configfs at setup removes previous daemon-managed DLM configfs state; this is intentional startup hygiene.
