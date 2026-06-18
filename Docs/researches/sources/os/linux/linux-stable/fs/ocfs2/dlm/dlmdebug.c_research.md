# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmdebug.c

## Purpose

`dlmdebug.c` provides diagnostic dumping and debugfs support for OCFS2 DLM state. It can print individual lock resources and locks, map DLM status codes to names, stringify lock names and node maps, and expose debugfs files for domain state, lock resources, master-list entries, and purge-list contents.

## Non-debugfs Diagnostics

Key functions:

- `dlm_print_one_lock_resource()` prints one lock resource with locking.
- `__dlm_print_one_lock_resource()` prints a lock resource while `res->spinlock` is already held.
- `dlm_print_one_lock()` exports lock-resource printing through a lock pointer.
- `dlm_errname()` exports human-readable names for `enum dlm_status`.
- `dlm_print_one_mle()` formats a master-list entry into a temporary page buffer.

The lock-resource dump includes:

- Lock name, owner, state, last-used timestamp, kref count.
- Purge, dirty, recovery, and migration flags.
- Inflight lock count and reserved AST count.
- Refmap nodes.
- Granted, converting, and blocked queues.
- Per-lock mode, convert mode, node, cookie, kref, AST/BAST state, and pending operation flags.

## Formatting Helpers

`stringify_lockname()` mostly emits the raw lock name, but has OCFS2-specific handling for names beginning with `N`, where it decodes an inode block number embedded in the name. This knowingly reaches beyond generic DLM semantics to make debug output more useful for OCFS2.

`stringify_nodemap()` emits set node numbers from a bitmap.

`dump_mle()` formats an MLE with:

- Lock name.
- Type: block, master, or migration.
- Current master and new master.
- Heartbeat event attachment.
- In-use flag and reference count.
- Maybe, vote, response, and node maps.

## Debugfs Files

When `CONFIG_DEBUG_FS` is enabled, the module creates a root directory named `o2dlm`, with one subdirectory per domain. Each domain gets:

- `dlm_state`
- `locking_state`
- `mle_state`
- `purge_list`

`dlm_state` prints domain-level information: key, negotiated protocol, thread pids, node number, DLM state, join state, domain maps, live maps, lock-resource and MLE counts, dirty/purge/AST lists, purge count, refcount, dead node, recovery master, recovery state, recovery map, and per-node recovery state.

`locking_state` is seq-file based and iterates `dlm->tracking_list`, dumping one lock resource at a time in a structured format with `NAME`, `LRES`, `RMAP`, `LVBX`, and `LOCK` records.

`mle_state` dumps all MLEs across the master hash and reports total count and longest bucket.

`purge_list` dumps lock resources on the purge list and their age in seconds.

## Concurrency

The debug code uses the same lock hierarchy as the DLM core:

- `dlm->spinlock` for domain state.
- `dlm->master_lock` for MLE hash traversal.
- `dlm->track_lock` for tracking list iteration.
- `res->spinlock` for lock-resource internals.
- `lock->spinlock` for individual lock state.

The lock-resource seq iterator holds and releases references across iterations to avoid use-after-free while walking the tracking list.

## Dependencies

This file depends heavily on structures and helpers from `dlmcommon.h`, plus debugfs, seq_file, kref, and OCFS2 cluster node/heartbeat infrastructure.
