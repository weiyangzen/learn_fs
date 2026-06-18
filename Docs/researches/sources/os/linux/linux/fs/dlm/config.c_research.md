# File Research: sources/os/linux/linux/fs/dlm/config.c

## Role

Implements DLM configfs configuration for clusters, lockspaces, communication endpoints, node membership, and global DLM tunables. Also exposes helper functions used by DLM runtime code to read configured nodes, comm sequence numbers, local node ID, and local addresses.

## Configfs Layout

The file documents the intended configfs hierarchy:

- `/config/dlm/<cluster>/spaces/<space>/nodes/<node>/nodeid`
- `/config/dlm/<cluster>/spaces/<space>/nodes/<node>/weight`
- `/config/dlm/<cluster>/spaces/<space>/nodes/<node>/release_recover`
- `/config/dlm/<cluster>/comms/<comm>/nodeid`
- `/config/dlm/<cluster>/comms/<comm>/local`
- `/config/dlm/<cluster>/comms/<comm>/addr`
- `/config/dlm/<cluster>/comms/<comm>/addr_list`

The cluster level mainly groups `spaces` and `comms`.

## Global State

- `space_list`: current configfs spaces group.
- `comm_list`: current configfs comms group.
- `local_comm`: configured local communication endpoint.
- `dlm_comm_count`: sequence generator for communication configs.
- `dlm_config`: global DLM tunable defaults and current values.

Also exports `dlm_rhash_rsb_params`, the resource rhashtable parameters used elsewhere by DLM.

## Configfs Object Types

Main structures:

- `dlm_cluster`: cluster group plus default `spaces` and `comms` groups.
- `dlm_space`: lockspace group, member lists, gone-member list, and lock.
- `dlm_comm`: communication endpoint, nodeid, local flag, addresses, mark, and sequence.
- `dlm_node`: lockspace member node, weight, new flag, comm sequence, release recovery marker.
- `dlm_member_gone`: deferred removal information for departed members.

Each has configfs operations for make/drop/release where applicable.

## Cluster Attributes

Cluster-wide tunables include:

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
- `cluster_name`

Writes to most numeric cluster attributes require `CAP_SYS_ADMIN`.

Validation includes:

- Non-zero checks for key timers/sizes.
- Minimum socket buffer size.
- Protocol limited to TCP or SCTP, with SCTP requiring `CONFIG_IP_SCTP`.
- Some communication settings are rejected with `-EBUSY` once lowcomms is running.

`cluster_name` is copied into the fixed-size config field.

## Cluster Creation

`make_cluster()` allocates cluster, spaces, and comms structures, initializes configfs groups, adds default `spaces` and `comms` groups, and records global pointers.

`drop_cluster()` removes default groups and clears global pointers.

`release_cluster()` frees allocated structures.

## Lockspace and Node Membership

`make_space()` allocates a lockspace group and default `nodes` subgroup, initializes member lists and mutex.

`make_node()`:

- Parses node ID from the configfs item name.
- Allocates a node record.
- Defaults weight to 1.
- Marks it as new.
- Captures current comm sequence for the node.
- Adds it to the lockspace member list.

`drop_node()`:

- Allocates a `dlm_member_gone` record.
- Removes the node from active members.
- Records nodeid and release recovery value in gone list.
- Defers reporting removal until `dlm_config_nodes()`.

This deferred removal exists because configfs `rmdir()` cannot carry extra removal attributes.

## Communication Endpoints

`make_comm()` parses node ID from the item name, allocates a comm item, assigns a nonzero sequence number, and initializes address count and mark.

`drop_comm()` clears `local_comm` if needed, closes midcomms for the node, frees stored addresses, and drops the item reference.

Communication attributes:

- `nodeid`: derived from item name.
- `local`: marks the endpoint as local if no local endpoint is set.
- `addr`: write-only binary `sockaddr_storage`; added through `dlm_midcomms_addr()`.
- `addr_list`: read-only formatted IPv4/IPv6 address list.
- `mark`: applies socket mark through `dlm_lowcomms_nodes_set_mark()`.

## Runtime Query Functions

`dlm_config_nodes()`:

- Looks up a lockspace by name.
- Requires nonzero member count.
- Allocates an array of `struct dlm_config_node`.
- Copies active members, including nodeid, weight, new flag, and comm sequence.
- Clears each member's `new` flag after reporting.
- Appends deferred gone members with `gone = true` and `release_recover`.
- Frees gone records after reporting.
- Returns allocated array and count to caller.

`dlm_comm_seq()` returns the current comm sequence for a node, optionally assuming the configfs subsystem mutex is already held.

`dlm_our_nodeid()` returns `local_comm->nodeid`.

`dlm_our_addr()` copies a configured local address by index.

## Defaults

Default configuration includes:

- TCP port `21064`.
- Buffer size `4096`.
- RSB table size `1024`.
- Recover timer `5`.
- Toss seconds `10`.
- Scan seconds `5`.
- Info logging enabled.
- Protocol TCP.
- New RSB count `128`.
- Empty cluster name.

## Important Invariants

- Runtime readers rely on configfs item references via `config_item_get()` / `config_item_put()`.
- `members_lock` protects lockspace active and gone member lists.
- `clusters_root.subsys.su_mutex` protects traversal of configfs children for comm lookup.
- Communication sequence numbers let nodes detect comm configuration changes.
- Only one `local_comm` is recorded.
- Gone nodes are reported once through `dlm_config_nodes()`.

## Research Notes

This file is the administrative bridge between userspace cluster configuration and DLM runtime membership/communication code. The highest-risk areas are configfs lifetime management, deferred node removal semantics, binary address input validation, and assumptions around `local_comm` being configured before use.
