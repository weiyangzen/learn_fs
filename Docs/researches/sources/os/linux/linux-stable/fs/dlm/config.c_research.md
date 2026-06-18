# File Research: sources/os/linux/linux-stable/fs/dlm/config.c

## Purpose

`config.c` implements DLM runtime configuration through configfs, exposing clusters, lockspaces, member nodes, communication endpoints, addresses, and cluster-wide tunables.

## Main Responsibilities

- Registers the `/config/dlm` configfs subsystem.
- Creates the configfs hierarchy:
  - `<cluster>/spaces/<space>/nodes/<node>/...`
  - `<cluster>/comms/<comm>/...`
- Stores global DLM configuration in `dlm_config`.
- Provides configfs attributes for cluster tunables, comm endpoints, and node membership.
- Tracks local communication endpoint and per-node communication sequence numbers.
- Maintains lockspace membership and delayed “gone” node records.
- Provides DLM-internal accessors for configured nodes, communication sequence, local node ID, and local addresses.
- Defines rhashtable parameters for DLM resource hash tables.

## Configfs Objects

- `dlm_cluster`: top-level cluster group containing default `spaces` and `comms` groups.
- `dlm_space`: lockspace group containing a default `nodes` group and member lists.
- `dlm_comm`: communication endpoint item with node ID, local flag, address list, mark, and sequence.
- `dlm_node`: lockspace member item with node ID, weight, new flag, communication sequence, and release-recover value.
- `dlm_member_gone`: transient record used to report removed members later.

## Cluster Attributes

- `cluster_name`
- `tcp_port`
- `buffer_size`
- `rsbtbl_size`
- `recover_timer`
- `toss_secs`
- `scan_secs`
- `log_debug`
- `log_info`
- `protocol`
- `mark`
- `new_rsb_count`
- `recover_callbacks`

Some attributes reject changes while low-level communications are running, and privileged writes require `CAP_SYS_ADMIN`.

## Communication and Node Attributes

Comm attributes:
- `nodeid`
- `local`
- `addr` write-only binary `sockaddr_storage`
- `addr_list` textual formatted address list
- `mark`

Node attributes:
- `nodeid`
- `weight`
- `release_recover`

## Key Control Flow

Setup:
- `dlm_config_init()` initializes and registers the configfs subsystem.
- `make_cluster()` creates cluster, spaces, and comms groups and stores global pointers to `space_list` and `comm_list`.
- `make_space()` creates a lockspace and its nodes subgroup.
- `make_comm()` creates a comm endpoint and assigns a nonzero sequence number.
- `make_node()` creates a lockspace member, snapshots the comm sequence, and adds it to the space member list.

Removal:
- `drop_comm()` clears `local_comm` if needed, closes midcomms for the node, frees stored addresses, and drops the item.
- `drop_node()` moves removed node information into `members_gone` so DLM can report removal with `release_recover`.
- `drop_cluster()` removes default groups and clears global group pointers.

Accessors:
- `dlm_config_nodes()` returns an allocated array of active and gone nodes for a lockspace, clears new flags, and drains gone records.
- `dlm_comm_seq()` returns a comm endpoint sequence number under configfs locking.
- `dlm_our_nodeid()` returns the configured local comm nodeid.
- `dlm_our_addr()` copies one configured local address.

## Important Dependencies

- configfs core.
- DLM midcomms and lowcomms for address registration, close, running-state checks, and mark updates.
- Linux networking address structures.
- Rhashtable infrastructure for resource table configuration.

## Edge Cases and Risks

- `space_list`, `comm_list`, and `local_comm` are global pointers tied to configfs object lifetime.
- `dlm_our_nodeid()` assumes `local_comm` exists; callers must ensure local comm setup has completed.
- `drop_node()` can fail to allocate `dlm_member_gone`; in that case removal reporting is skipped.
- `addr` writes require exactly `sizeof(struct sockaddr_storage)` binary input and cap addresses at `DLM_MAX_ADDR_COUNT`.
- Protocol changes are rejected while lowcomms are running and SCTP requires `CONFIG_IP_SCTP`.
- `dlm_config_nodes()` returns heap memory that callers must free.
