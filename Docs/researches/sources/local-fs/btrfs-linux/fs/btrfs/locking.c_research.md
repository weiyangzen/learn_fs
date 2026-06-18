# File Research: sources/local-fs/btrfs-linux/fs/btrfs/locking.c

## Purpose

Implements Btrfs extent-buffer tree locking and the DREW lock used for A-B exclusion without excluding same-side readers/writers.

## Main Responsibilities

- Defines debug lockdep keysets per tree root objectid and B-tree level.
- Assigns extent-buffer lock classes to avoid false lockdep reports across roots and B-tree levels.
- Wraps extent-buffer read/write locking with tracing and optional debug owner tracking.
- Provides root-node lock acquisition loops that retry if the root node changes while acquiring the lock.
- Provides safe path unlock helpers.
- Implements `btrfs_drew_lock`, used where two operation classes must exclude each other but same-class operations may coexist.

## Key Behaviors and Invariants

- Lockdep classes assume `BTRFS_MAX_LEVEL == 8`; the file has a compile-time guard.
- Root-node lock helpers take a reference, lock, verify it is still the current root node, otherwise unlock/free/retry.
- DREW lock gives priority to readers: pending readers prevent new writers from settling.
- Atomic barriers around DREW counters ensure waiters observe state transitions before sleeping/waking.
