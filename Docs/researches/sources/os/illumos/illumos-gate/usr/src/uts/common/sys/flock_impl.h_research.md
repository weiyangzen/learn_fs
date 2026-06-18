# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/flock_impl.h

This header defines the private in-kernel implementation structures and macros for illumos file/record locking. It is not the public `flock` API; it describes the local lock manager’s graph model, lock lifecycle, dependency tracking, and process-level deadlock detection support.

Key structures:
- `edge_t` models dependency edges between lock descriptors, with both adjacency and incoming-edge list links.
- `lock_descriptor_t` represents an active, sleeping, granted, interrupted, cancelled, or dead lock request. It stores vnode, range, original `flock64_t`, owner/process metadata, NLM state, zone, optional OFD-style file reference, callback hooks, graph links, and wait condition variable.
- `graph_t` owns per-hash-bucket lock state: a mutex, circular active/sleeping lock lists, graph index, and traversal mark.
- `proc_vertex_t`, `proc_edge_t`, and `proc_graph_t` model process dependency graphs used for deadlock detection across lock owners.

Important constants and state:
- `FLK_INITIAL_STATE` through `FLK_DEAD_STATE` define the lock lifecycle. The comment documents allowed transitions and the functions or wakeups responsible for each transition.
- Legacy `l_state` bit flags include `ACTIVE_LOCK`, `SLEEPING_LOCK`, `IO_LOCK`, `QUERY_LOCK`, `LOCKMGR_LOCK`, `PXFS_LOCK`, and `NBMAND_LOCK`.
- `HASH_SIZE` is 32, and `HASH_INDEX(vp)` hashes vnodes into lock graphs.
- `PXFS_LOCK_BLOCKED` is a special `reclock()` result for blocking PXFS lock requests.

Core macros:
- Owner/range tests include `SAME_OWNER`, `PROC_SAME_OWNER`, `OVERLAP`, `BLOCKS`, and `COVERS`.
- Status predicates include `IS_ACTIVE`, `IS_SLEEPING`, `IS_GRANTED`, `IS_INTERRUPTED`, `IS_CANCELLED`, and `IS_DEAD`.
- Queue/list macros manipulate active/sleeping lists and graph edge lists.
- Wakeup macros `GRANT_WAKEUP`, `CANCEL_WAKEUP`, and `INTERRUPT_WAKEUP` update status bits and signal waiters, except for PXFS locks, which do not sleep in the local lock manager.
- `COPY` copies selected lock request fields, including graph, vnode, type, byte range, flock payload, zone, and process vertex.

External interface:
- Exposes internal lock graph state through `lock_graph[HASH_SIZE]` and `flk_edge_cache`.
- Declares lock-manager routines used by PXFS: `flk_execute_request`, `flk_cancel_sleeping_lock`, `flk_set_state`, and `flk_get_lock_graph`.
- Declares `cl_flk_state_transition_notify()`, a weak-stub style callback for the PXFS server module.
- Declares global `pgraph`.

Dependencies and relationships:
- The file bridges local vnode byte-range locking, NFS/NLM state, PXFS cluster locking, and process-level deadlock detection.
- `l_ofd` participates in ownership identity, so OFD-style locks are distinguished even with the same pid/sysid.
- Many definitions are tightly coupled to `flock.c` and private lock manager invariants.
