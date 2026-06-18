# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_witness.c

Implements WITNESS, OpenBSD’s kernel lock-order verifier. It enrolls lock objects by lock type/subtype/class, tracks locks currently held by threads and CPUs, records observed lock-order edges, detects lock-order reversals and misuse, supports optional stack traces, and exposes debugger/sysctl controls.

Main model types include `struct lock_class`, `struct witness`, `struct lock_instance`, `struct lock_list_entry`, witness hash tables, lock-order-data hash tables, and per-CPU witness caches. Sleep locks are tracked per thread in `p_sleeplocks`; spin locks are tracked per CPU in `witness_cpu[].wc_spinlocks`. Relationship state is stored in `w_rmatrix`, with flags for parent/ancestor/child/descendant/reversal/known-order.

`witness_initialize()` boot-allocates witness objects, relationship matrix rows, lock-list entries, optional lock stack storage, initializes free lists and hashes, enrolls pending cold-boot locks, and marks WITNESS usable. `witness_init()` validates lock flags against class capabilities, defers or enrolls locks, or disables witness tracking for uninteresting locks.

`witness_checkorder()` is the main pre-acquire verifier. It handles uninitialized lock reporting, enrolls missing witnesses, enforces no sleep locks while spin locks are held, handles recursion/exclusive/shared mismatch checks, validates interlocks, quickly accepts known direct orders, records new observed orders, detects duplicate same-type locks unless allowed, checks all already-held locks for reversals, handles special kernel-lock/sleepable rules, suppresses known vnode-vnode reversal noise, prints cycle information, and optionally enters DDB.

`witness_lock()` records a successfully acquired lock in the appropriate held-lock list, including recursion count and optional stack trace. `witness_unlock()` validates unlock mode, recursion, no-release flags, stack cleanup, and list removal. `witness_upgrade()` and `witness_downgrade()` validate shared/exclusive state transitions for upgradable sleep locks.

Graph maintenance is handled by `itismychild()` and `adopt()`, which add direct parent-child relationships and propagate ancestor/descendant transitive closure through `w_rmatrix`. Inconsistencies disable witness. `witness_lock_order_add()` stores a known direct order and stack trace in `w_lohash`; `witness_lock_order_check()` fast-paths known valid relations.

Diagnostics include `witness_warn()` for “locks held here” checks, `witness_assert()` for lock assertion semantics, `witness_thread_exit()` panic-on-exit-with-locks, `witness_display_spinlock()` for suspected spinlock owner inspection, `witness_norelease()`/`witness_releaseok()`, DDB list/display/fullgraph/bad-stack commands, and cycle printing with short path search.

Runtime controls are through `witness_sysctl()` and `witness_sysctl_watch()`. `witness_watch` ranges from disabled forever to checking/dump/debugger modes; `witness_locktrace` can be enabled if stack buffers can be allocated.

Filesystem relevance: WITNESS is central to validating VFS, vnode, buffer-cache, and filesystem lock ordering. The code explicitly recognizes vnode lock-order reversals as a known noisy class and suppresses escalation for vnode-vnode LORs while still recording the relationship.
