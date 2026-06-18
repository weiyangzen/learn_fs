# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_lock.c

## Summary
Implements vnode lifecycle, reference handling, activation/inactivation state transitions, VX locking, vnode allocation, recycling, and pressure reclamation.

## Main Responsibilities
- Initializes per-CPU-ish vnode active/inactive lists.
- Tracks active, cached, and inactive vnode counts.
- Implements `vref()`, `vrele()`, `vhold()`, `vdrop()`, and `vfinalize()`.
- Implements VX lock helpers used for reclamation and deactivation.
- Reactivates vnodes with `vget()` and releases locked vnodes with `vput()`.
- Allocates/reuses vnodes in `allocvnode()` and frees pressure candidates through `freesomevnodes()`.

## Important Behavior
Vnodes move among `VS_ACTIVE`, `VS_INACTIVE`, `VS_CACHED`, and `VS_DYING` under carefully documented lock requirements. `vrele()` has a fast lockless decrement path for non-final references, but on a finalizing 1-to-0 transition it acquires the VX lock and calls `vnode_terminate()`.

`cleanfreevnode()` first tries to rebalance active cached vnodes into inactive state, then scans inactive lists for reclaimable candidates. It avoids recycling vnodes with unexpected aux refs, active namecache topology, active real refs, or lock contention. Reusable vnodes are transitioned to `VS_DYING` and returned VX-locked.

## Risks
This is highly concurrency-sensitive code with many invariants around `v_refcnt`, `v_auxrefs`, namecache references, and list state. Several comments note races or limitations, including object races in deactivation weighting and an abandoned alternative `vrele()` implementation that was not safe.
