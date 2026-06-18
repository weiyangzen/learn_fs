
# sources/user-network-fs/nfs-ganesha/src/SAL/recovery/recovery_rados_cluster.c

## Purpose

`recovery_rados_cluster.c` implements the clustered RADOS recovery backend. It coordinates cluster-wide NFSv4 grace epochs through the rados-grace object, creates epoch-scoped recovery omap objects, handles node/IP takeover, and can start local grace when another cluster member triggers a new global grace period.

## Important APIs, types, and functions

- Static state: `takeover`, `object_takeover`, `object_takeover_old`, `object_ipbased`, `rados_watch_cookie`, `addr_int`, and global epoch values `cur` and `rec`.
- `rados_cluster_init()` sets node id, configures optional IP-based identity, connects to RADOS, verifies grace membership, and installs a watch on the grace object.
- `rados_grace_watchcb()` acknowledges RADOS notifications and wakes grace waiters/reaper.
- `rados_cluster_read_clids()` joins grace, creates the current epoch recovery object, chooses the old/takeover object, and traverses reclaim clients with `rados_ng_pop_clid_entry()`.
- `rados_cluster_add_clid()` and `rados_cluster_rm_clid()` write/remove clients in the current epoch object or per-client IP-based object.
- `rados_cluster_end_grace()` turns off enforcing in rados-grace and removes the old/takeover recovery object.
- `rados_cluster_maybe_start_grace()` detects remote grace epochs, snapshots current confirmed clients into a new object, and calls `nfs_start_grace()`.
- `rados_cluster_try_lift_grace()`, `rados_cluster_set_enforcing()`, `rados_cluster_grace_enforcing()`, and `rados_cluster_is_member()` wrap rados-grace state transitions/checks.
- `rados_cluster_backend` exposes the full clustered backend hook table.

## Control flow

Initialization calls shared `set_nodeid()`, optionally converts `g_node_vip` to an integer `ip_%d` identity, connects to RADOS, verifies this node is in the grace table, and starts watching `rados_kv_param.grace_oid`. Watch callbacks do not process records directly; they wake existing NFS grace/reaper mechanisms.

On recovery read, the backend optionally configures takeover target names from `nfs_grace_start_t`. It then calls `rados_grace_join()` to enter or join a grace period and receives current and recovery epochs. It creates a new current object named `rec-%16.16lx:<identity>` for `cur`, clears its omap, and sets `rados_recov_oid`. It then traverses the previous epoch object for `rec`, either for this node/IP or the takeover identity, and populates in-memory recovery clients.

When the local server observes that a remote grace period is already active, `rados_cluster_maybe_start_grace()` creates a new current object and snapshots all currently confirmed clients into it. This allows the local server to participate in the new grace without losing active clients.

End grace disables enforcing for this node and deletes the old recovery object. Shutdown starts/join grace to protect clean shutdown windows, unwatches the grace object, shuts down RADOS, and frees node state.

## State and persistence behavior

Recovery client records live in RADOS omap objects whose names include the grace epoch and identity. The clustered grace object tracks membership and epochs separately through the rados-grace library. IP-based recovery can use object names based on an integer form of the VIP or per-client server address hash, while normal mode uses hostname or `node%d`.

The backend uses RCU-protected `gsh_refstr` object names because add/remove operations may run concurrently with epoch switches. Values are the shared RADOS KV format parsed by `rados_ng_pop_clid_entry()`.

## Dependencies and integration points

The file depends on librados, `rados_grace.h`, shared RADOS KV helpers, global client hash `ht_confirmed_client_id`, NFS grace APIs (`nfs_start_grace`, `nfs_notify_grace_waiters`, `reaper_wake`), and optional FSAL reclaim hook `nfs_recovery_fsal_reclaim_client()` for Ceph nodeid takeover. It integrates with SAL through `struct nfs4_recovery_backend`.

## Risks and edge cases

- `rados_set_client_cb()` has a fixed 1024-entry cap and logs rather than resizing, so large client populations can be incompletely snapshotted during remote grace.
- IPv6 conversion uses the lower 32 bits of the address for integer identity; collisions are possible.
- IP-based object naming differs between init/takeover (`ip_%d`) and per-client add/remove (`rec-epoch:ip_<hash>`), so tests must verify intended semantics.
- Error handling often logs and continues, which can leave grace joined but object creation/traversal incomplete.
- Shutdown intentionally joins grace; failures there are logged but cannot guarantee external MDS/session protection.
- RCU pointer exchange and reference handling are central; missed refs could lead to stale object-name use during epoch transitions.

## Test signals

Cluster tests should cover join/lift grace, grace enforcement on/off, notification watch callbacks, local restart recovery, nodeid takeover, IP takeover, remote grace start with confirmed clients, object cleanup after grace, membership loss, and >1024 clients. Fault injection should cover RADOS connection failures, object create/remove failures, rados-grace API failures, and concurrent add/remove during epoch changes.
