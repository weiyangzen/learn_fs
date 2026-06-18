# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_lockf.c

## Purpose
Implements advisory byte-range locking for vnode operations, covering POSIX `fcntl` locks, BSD `flock` locks, remote locks, async lock requests, deadlock detection, lock reporting, and remote-system cleanup.

## Key Interfaces
- `lf_advlockasync()` is the primary async lock operation handler.
- `lf_advlock()` adapts synchronous VOP advlock requests.
- `lf_purgelocks()` clears all locks for a doomed vnode.
- `lf_clearremotesys()` and `lf_countlocks()` manage remote lock owners by system id.
- `lf_iteratelocks_sysid()` and `lf_iteratelocks_vnode()` iterate locks for cleanup.
- `vfs_report_lockf()` and `sysctl kern.lockf` export lock state.

## State And Locking
Each vnode can reference a `struct lockf` state with active and pending lists guarded by `ls_lock`. Global `lf_lock_states` is guarded by `lf_lock_states_lock`. Lock owners are hashed across 256 sx-protected chains. A global owner graph guarded by `lf_owner_graph_lock` tracks wait-for dependencies and uses dynamic topological sorting to reject cycles.

## Control Flow
Requests convert `flock` offsets into inclusive `[start,end]` ranges, create or find a lock owner, allocate a lock entry, create vnode state as needed, and dispatch set/unlock/get/cancel. Set-lock scans active locks for blockers. Blocking synchronous requests sleep on the lock entry; async requests return `EINPROGRESS` and a cookie. Unlock and same-owner lock changes use overlap classification to remove, shrink, split, or replace active locks, waking newly unblocked pending locks.

## Deadlock Handling
Per-vnode lock edges represent pending locks blocked by active or older pending locks. The global owner graph maps those edges to owner-to-owner waits. `graph_add_edge()` maintains topological order using forward/backward delta sets and returns `EDEADLK` if adding an edge would create a cycle.

## Risks
Correctness depends on keeping vnode active lists sorted, edge lists synchronized with the owner graph, and references balanced for remote vnode locks. `EDOOFUS` is used internally to retry after a sleeping lock object was consumed. Async cancel uses the lock pointer as a cookie and validates vnode/range before cancellation.
