# sources/storage-engines/wiredtiger/src/include/ref_inline.h

## Purpose
Defines the controlled API for reading, writing, CASing, locking, and unlocking `WT_REF` page-reference states, plus a helper for detecting root references.

## Important APIs, Types, And Functions
- `__wt_ref_is_root` treats a ref with null `home` as the root reference.
- `__ref_set_state` writes the ref state with a release barrier.
- `WT_REF_SET_STATE` wraps state writes and optionally records diagnostic history with `HAVE_REF_TRACK`.
- `__ref_get_state` and `WT_REF_GET_STATE` read the volatile state with relaxed atomics.
- `__ref_cas_state` and `WT_REF_CAS_STATE` CAS from an old to new state and optionally record callsite history.
- `__ref_lock`/`WT_REF_LOCK` spin until the state becomes `WT_REF_LOCKED`, returning the previous state.
- `__ref_try_lock`/`WT_REF_TRYLOCK` attempt one lock transition.
- `WT_REF_UNLOCK` restores a previous state through `WT_REF_SET_STATE`.

## Control Flow
Locking repeatedly reads the current state, yields between attempts, and CASes any non-locked state to `WT_REF_LOCKED`. Trylock performs a single read/CAS and returns `EBUSY` if already locked or if the CAS loses a race. Diagnostic tracking stores session, function, line, timestamp, and state in a ring without strict synchronization to avoid hot-path overhead.

## State And Persistence Behavior
The ref state is volatile in-memory page-tree state controlling access to pages and their lifecycle. It is not persistent itself, but it protects loading, eviction, split, and reconciliation behavior for persistent pages.

## Dependencies And Integration Points
Depends on `WT_REF`, `WT_REF_STATE`, atomics, TSan suppression helpers, barriers, session diagnostics, yield, and `WT_ASSERT`. Used by page eviction, tree walking, hazard handling, reconciliation, and page split logic.

## Risks
Direct access to `ref->__state` outside these macros breaks synchronization and diagnostics. Relaxed reads are acceptable only within the documented state protocol. Diagnostic history intentionally races and cannot be treated as authoritative under contention. Locking spins, so callers must avoid holding refs locked for long operations.

## Test Signals
Concurrency tests should cover CAS state transitions, lock/trylock contention, unlock restoring previous states, root-ref detection, ref tracking history in diagnostic builds, and TSan runs for page-tree operations.
