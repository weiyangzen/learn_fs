# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/flock.c

## Purpose

`flock.c` implements illumos kernel record locking: traditional POSIX byte-range locks, open-file-description locks, mandatory-lock I/O checks, NFS/NLM lock-manager integration, PXFS/cluster lock state, and deadlock detection.

Read completely: 4,609 lines.

## Main Responsibilities

- Handles POSIX-style process-owned record locks through `reclock()`.
- Handles open-file-description locks through `ofdlock()` and `ofdcleanlock()`.
- Maintains vnode-hashed lock dependency graphs in `lock_graph[HASH_SIZE]`.
- Tracks active and sleeping locks per graph and wakes blocked requests when dependencies clear.
- Splits, coalesces, upgrades, downgrades, and deletes byte-range locks owned by the same owner.
- Performs process-level deadlock detection with a separate process dependency graph.
- Supports lock-manager shutdown/startup state per zone and per lock graph.
- Supports cluster/NLM state transitions and remote-lock cleanup by sysid, nlmid, and PXFS id.
- Implements mandatory-lock probes used by filesystem read/write/mmap paths.
- Builds lock snapshots for NLM reclaim and administrative queries.

## Lock Models

`reclock()` is the main POSIX record-lock entry point used by filesystem `frlock` paths. It validates permissions, canonicalizes ranges, handles local, remote, PXFS, I/O, blocking, nonblocking, and query requests, then dispatches through the lock graph.

`ofdlock()` implements open-file-description locking. These locks are tied to `file_t` through `f_filock`, use `l_ofd` for ownership, preserve locks across fork, avoid process-based deadlock detection, and currently require whole-file lock ranges as validated by the fcntl layer.

`cleanlocks()` removes non-OFD locks for a vnode/pid/sysid during close/exit style cleanup. OFD cleanup is separate in `ofdcleanlock()` because the lock belongs to the file description, not only the process.

## Dependency Graph

Each vnode hashes to a `graph_t`, protected by `gp_mutex`. Active locks are sorted by vnode and range. Sleeping locks are sorted by vnode. Requests that cannot proceed acquire directed edges to blocking locks.

Important routines:

- `flk_process_request()` decides whether a request can run, should fail with `EAGAIN`, should sleep, or would deadlock.
- `flk_execute_request()` applies the request and inserts active locks when needed.
- `flk_relation()` handles same-owner overlap, adjacent coalescing, unlock splitting, downgrade, and upgrade effects.
- `flk_add_edge()` adds graph edges and optionally checks lock-level cycles.
- `flk_recompute_dependencies()` repairs dependency edges after a lock is modified or removed.
- `flk_wakeup()` grants sleeping locks once all dependencies are gone.
- `flk_cancel_sleeping_lock()` removes a sleeping request and recomputes affected dependencies.

The graph is deliberately kept minimal: edges are not added when an existing path already represents the dependency.

## Deadlock Detection

`flk_check_deadlock()` projects lock dependencies onto a process graph keyed by pid/sysid. It creates `proc_vertex_t` and `proc_edge_t` records, tracks reference counts for multiple lock edges between the same owners, and detects cycles by graph traversal.

OFD locks skip this path because they are pid-less. That is an intentional semantic difference from POSIX locks and matches the file’s comments.

## Lock Manager And Cluster Paths

The file maintains per-zone lock manager state in `struct flock_globals`. `flk_set_lockmgr_status()` transitions the lock manager through up, wake-sleepers, and down states, waking or removing relevant NLM locks for the current zone.

Cluster support keeps an NLM status registry indexed by nlmid. Routines such as `cl_flk_set_nlm_status()`, `cl_flk_wakeup_sleeping_nlm_locks()`, `cl_flk_unlock_nlm_granted()`, `cl_flk_remove_locks_by_sysid()`, and `cl_flk_delete_pxfs_locks()` synchronize remote lock state with NLM or PXFS failure/recovery.

## Mandatory Locking And Filesystem Relevance

`chklock()` issues an internal lock probe for read/write paths on mandatory-lock files.

`nbl_lock_conflict()` checks active NBMAND or SVMAND locks against I/O ranges and is directly used by higher-level file access and mapping enforcement. `lock_blocks_io()` contains the final range/type conflict rule.

`convoff()`, `flk_convert_lock_data()`, and `flk_check_lock_data()` normalize and validate byte ranges, including EOF-relative and negative-length locks.

## Important Invariants

- Most lock graph operations require `gp_mutex`.
- Global graph-table and process-graph updates use `flock_lock`.
- Active locks must not block each other.
- Sleeping locks must have dependency paths to active or earlier sleeping blockers.
- `flk_set_state()` enforces ordered wake states: interrupted outranks cancelled, cancelled outranks granted.
- Remote lock-manager requests can cover ranges beyond local signed `MAXEND`, so blocker reporting must translate ranges carefully.

## Research Relevance

This is the central illumos file-locking implementation that filesystem code depends on for `fcntl`, NFS lock recovery, mandatory locking, mmap conflict checks, and vnode lock-list snapshots. It is highly relevant to VFS/filesystem semantics, especially where locks interact with close, fork, remote filesystems, and memory mappings.
