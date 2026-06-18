# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_witness.c

## Purpose

Implements FreeBSD's WITNESS lock-order verifier. It tracks lock classes, lock acquisition order, held-lock stacks, and known lock-order relationships to detect deadlock-prone lock order reversals, invalid recursion, invalid upgrades/downgrades, sleeping with locks held, and other locking contract violations.

## Main responsibilities

- Enrolls named lock types into `struct witness` records.
- Tracks lock instances held by threads or CPUs.
- Maintains a relationship matrix describing parent/child and ancestor/descendant lock ordering.
- Records lock-order establishment stack traces.
- Detects duplicate lock acquisition and lock-order reversals.
- Provides warnings, panics, debugger entry, sysctls, and DDB commands.
- Encodes static order rules for major kernel subsystems.

## Key data structures

- `struct witness`
  - One per named lock type.
  - Stores name, class, matrix index, refcount, last acquire site, graph counters, and reversal flags.
- `struct lock_instance`
  - Per held lock: lock pointer, source file/line, exclusive/shared state, recursion count, no-release flag, sleepable state.
- `struct lock_list_entry`
  - Chunked list for locks held by a thread or CPU.
- `w_rmatrix`
  - Relationship matrix with parent/child, ancestor/descendant, reversal, hardcoded-order, and known-order bits.
- `struct witness_lock_order_data`
  - Hash-table entry storing stack trace for a direct lock order.
- Static `order_lists`
  - Hardcoded lock order chains for sx locks, mutexes, sockets, routing, multicast, UNIX sockets, UDP/TCP, BPF, NFS, VM, VFS/namecache, ZFS, spin locks, and leaf locks.
- `blessed_list`
  - Known tolerated pairs such as `dirhash`/`bufwait`, `ufs`/`bufwait`, and `tarfs`/`bufwait`.

## Important control flow

- `witness_startup_count()` computes early boot memory needed for witness objects and matrix storage.
- `witness_startup()` initializes WITNESS, preloads static order lists, enrolls pending locks, initializes hash tables, and enables runtime checking.
- `witness_init()` validates lock flags against lock class capabilities and enrolls or defers lock witness setup.
- `witness_checkorder()` is the core verifier:
  - Rejects sleep-lock acquisition while in critical/spin context.
  - Checks recursive shared/exclusive mismatches.
  - Validates interlock expectations.
  - Checks recently held and all held locks against the lock graph.
  - Records new orders and reports reversals with stack traces.
- `witness_lock()` records a lock as held.
- `witness_unlock()` validates unlock mode, handles recursion, rejects forbidden release, and removes the instance.
- `witness_upgrade()` and `witness_downgrade()` enforce upgradable sleep-lock semantics.
- `adopt()` and `itismychild()` add direct lock-order edges and propagate transitive ancestor/descendant relationships.
- `witness_warn()` reports locks held at unsafe sleep/blocking points.
- `witness_assert()` and `witness_is_owned()` support lock assertion checks.

## Debug and observability

- Sysctls under `debug.witness`:
  - `watch`
  - `kdb`
  - `trace`
  - `skipspin`
  - `output_channel`
  - `fullgraph`
  - `badstacks`
- DDB commands:
  - `show locks`
  - `show alllocks`
  - `show witness`
  - `show badstacks`
- Verbose graph reporting walks lock chains and prints stack traces for known order paths.

## Filesystem/storage relevance

This file is central to safe VFS and filesystem locking. The hardcoded order lists explicitly include VFS, namecache, vnode interlock, mount mutex, UFS/tarfs blessed buffer-lock interactions, VM object/page locks, and ZFS lock names. It does not implement file I/O, but it guards correctness of filesystem and VM lock ordering.

## Edge cases and safeguards

- WITNESS disables itself on witness object or lock-list exhaustion.
- Spin-lock tracking is optional via `witness_skipspin`.
- Graph generation counters help sysctl reporting restart if the lock graph changes.
- Some checks are done lockless first for performance, then repeated under `w_mtx`.
- The matrix has consistency checks for paradoxical ancestor/descendant states.
- `witness_watch = -1` permanently disables WITNESS until reboot.

## Research notes

Classify this as kernel lock verification infrastructure. For filesystem research, its most important sections are the hardcoded VFS/namecache/VM/ZFS order lists, blessed filesystem-buffer lock pairs, and public assertion/warning APIs used by lock primitives.
