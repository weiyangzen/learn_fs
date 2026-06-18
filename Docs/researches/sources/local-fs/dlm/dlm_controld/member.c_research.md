# File Research: sources/local-fs/dlm/dlm_controld/member.c

This file connects `dlm_controld` to Corosync quorum/cfg/cmap APIs and translates cluster membership into DLM configfs node state.

Key state:
- Corosync cfg handle `ch` and quorum handle `qh`.
- Old and current quorum node arrays.
- A list of `struct node_cluster` records containing node id, cluster add time, and remove time.
- A `leavejoin_nodes` array for nodes that appear in both joined and left lists in one ring transition.

Key behavior:
- `quorum_nodelist_callback()` logs joined/left nodes and records leave-join nodes.
- `quorum_callback()` updates quorate/ring state, tracks add/remove times, removes configfs nodes for departed members, handles leave-join as remove-plus-add, and creates configfs comms nodes for new members using Corosync node addresses.
- `cluster_add_time()` exposes a node’s add timestamp.
- `is_cluster_member()` checks current quorum list.
- `process_cluster()` and `update_cluster()` dispatch quorum callbacks.
- `setup_cluster()` initializes quorum model v1 tracking and returns its fd for the main poll loop.
- `setup_cluster_cfg()` initializes cfg, retries transient startup failures, gets cfg fd and local node id, and rejects negative node ids.
- `kick_node_from_cluster()` asks Corosync to shut down locally or kill a remote node.
- `shutdown_callback()` allows Corosync shutdown only when no lockspaces are active.
- `setup_node_config()` reads Corosync cmap nodelist entries, adds startup-fencing nodes when enabled, and detects two-node quorum mode.

Important dependencies:
- Calls `add_configfs_node()` and `del_configfs_node()` to mirror membership into kernel DLM configfs.
- Uses `node_config_get()` to apply per-node marks.
- Uses global daemon state: `our_nodeid`, `cluster_quorate`, `cluster_ringid_seq`, `cluster_two_node`, `cluster_joined_*`, `fence_delay_begin`, and lockspace list.
- Uses fencing startup hooks such as `add_startup_node()`.

Notable details:
- The code copies old quorum membership before replacing it, then computes removals/additions by array scans.
- The address pointer `addrptr` points to the stack `addrs` array and is indexed for every address returned by Corosync.
- `setup_node_config()` treats cmap failure to read `quorum.two_node` as non-fatal.
