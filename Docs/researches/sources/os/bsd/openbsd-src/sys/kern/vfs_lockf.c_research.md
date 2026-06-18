# File Research: sources/os/bsd/openbsd-src/sys/kern/vfs_lockf.c

Read completely: 904 lines.

Implements OpenBSD advisory byte-range locking for vnode-backed files and special devices. It supports POSIX `fcntl` locks and BSD `flock` semantics, storing sorted lock ranges in a per-vnode `lockf_state` protected by a global rwlock.

Core structures and limits:
- `struct lockf` records lock flags, type, inclusive start/end byte range, owner id, lock state, active/pending list links, blocking relationships, charged uid, and reporting pid.
- `struct lockf_state` owns active locks, pending locks, a backpointer to the vnode/special-device owner pointer, and a reference count.
- `lockf_lock` serializes all lock and state operations.
- `lf_init()` initializes pools for lock states and locks.
- `lf_alloc()` charges `uidinfo.ui_lockcnt` and enforces `maxlocksperuid`, with looser limits for unlock-time splitting.
- `ls_ref()` and `ls_rele()` manage state lifetime and clear the owner pointer when the last reference disappears.

External operation path:
- `lf_advlock()` normalizes `struct flock` `l_whence`, `l_start`, and `l_len` into inclusive ranges, including negative lengths and EOF locks represented by `lf_end == -1`.
- It creates a lock state on first use, allocates a candidate lock, fills POSIX pid reporting when needed, and dispatches `F_SETLK`, `F_UNLCK`, or `F_GETLK`.
- `F_SETLK` calls `lf_setlock()`, `F_UNLCK` calls `lf_clearlock()`, and `F_GETLK` calls `lf_getlock()`.

Range matching and mutation:
- `lf_findoverlap()` walks sorted locks and classifies overlap into six cases: none, exact, existing contains requested, requested contains existing, existing starts before, or existing ends after.
- `lf_getblock()` finds the first conflicting lock owned by another id, allowing read/read overlap.
- `lf_setlock()` waits for conflicts when `F_WAIT` is set, optionally detects POSIX deadlocks, removes shared flock locks before exclusive flock upgrades, and then inserts/merges/splits/replaces same-owner overlapping ranges.
- `lf_clearlock()` removes or shrinks same-owner locks and wakes waiters affected by the changed range.
- `lf_split()` splits an existing lock around a contained new or unlocked range, allocating a third range when needed.
- `lf_wakelock()` wakes every waiter blocked on a given lock and can mark interrupted purges.
- `lf_purgelocks()` interrupts pending locks, waits for them to exit, then removes all active locks for a state.

Deadlock and diagnostics:
- `lf_deadlock()` checks pending POSIX locks for a simple two-party cycle involving the current lock and a blocking owner.
- `LOCKF_DEBUG` includes lock/list printing helpers and debug categories.

Risks and notes:
- The global `lockf_lock` is simple but makes lock-list mutation, sleeping, waking, and state reference counts tightly coupled.
- Deadlock detection is limited and intentionally much simpler than full graph detection.
- EOF range representation with `-1` makes arithmetic and overlap ordering subtle.
- `lf_split()` may allocate while handling an unlock, so allocation-limit exceptions are part of correctness.
- `lf_purgelocks()` depends on pending waiters clearing `ls_pending` and waking the state before final free.
