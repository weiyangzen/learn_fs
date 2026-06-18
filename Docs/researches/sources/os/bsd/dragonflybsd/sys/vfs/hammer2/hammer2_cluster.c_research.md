# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_cluster.c

## Purpose
Implements basic HAMMER2 cluster object operations over multiple per-node chains, including focus selection, ref/drop/lock wrappers, and quorum validation for multi-master or master/slave cluster views.

## Key Elements
- File-level comments describe the intended cluster abstraction: collect chains from multiple nodes into one frontend topology, handle I/O dispatch/status rollup/mastership/quorum, and provide chain-like APIs to vnops.
- `hammer2_cluster_type()` returns the focused chain's blockref type or empty type when the cluster is errored.
- `hammer2_cluster_bref()` copies the focus blockref but clears `data_off`, because physical offsets are per-node and not useful to the frontend cluster view.
- `hammer2_dummy_xop_from_chain()` builds a degenerate one-chain cluster/xop from a locked chain, transferring the chain lock/reference into the cluster and marking hard read/write and sync flags.
- `hammer2_cluster_ref()` increments the cluster reference count.
- `hammer2_cluster_drop()` releases the final cluster reference, drops all underlying chains, clears safety fields, and frees the cluster allocation.
- `hammer2_cluster_lock()` locks all underlying chains with the requested chain lock mode and marks the cluster locked without re-resolving focus.
- `hammer2_cluster_unhold()` and `hammer2_cluster_rehold()` apply chain unhold/rehold to all underlying chains.
- `hammer2_cluster_check()` is the core resolver. It counts total masters/slaves, determines quorum, selects the highest matching quorum `modify_tid`, returns `EINPROGRESS`, `ESRCH`, `EDEADLK`, `ENOENT`, `EIO`, or chain/check errors as appropriate, marks valid/invalid cluster items, chooses focus/focus index, sets read/write hard/soft and master/slave sync flags, and validates that non-focus matching items have the same type/key/keybits/modify_tid/bytes/ddflag.
- `hammer2_cluster_unlock()` clears the locked flag and unlocks all underlying chains.

## Dependencies
Uses `hammer2_chain_*` lifecycle/lock APIs, HAMMER2 PFS type arrays, cluster/citem flags, HAMMER2 error codes, atomic flag operations, and kernel assertions/printing.

## Behavior/Risks
- The implemented file is narrower than the extensive file header suggests; asynchronous xops and network dispatch live elsewhere, while this file mainly handles local cluster state/focus/quorum.
- `hammer2_cluster_check()` has several explicit TODO/XXX notes around soft master/slave handling and cumulative error behavior.
- Focus selection depends on quorum among masters and matching `modify_tid`; desynchronized nodes can yield `EINPROGRESS`, `ESRCH`, or `EDEADLK` instead of a usable focus.
- Cluster consumers must respect the locked/refcount contract. The dummy-xop constructor transfers ownership of the chain lock/reference, so callers must not unlock/drop that chain separately.
