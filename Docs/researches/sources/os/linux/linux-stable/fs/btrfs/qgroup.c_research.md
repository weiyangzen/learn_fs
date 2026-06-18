# File Research: sources/os/linux/linux-stable/fs/btrfs/qgroup.c

This file implements Btrfs qgroups: quota groups for referenced/exclusive accounting, reservation enforcement, qgroup hierarchy management, rescan, simple quota support, and relocation-related delayed subtree accounting.

Quota modes:
- `btrfs_qgroup_mode()` returns disabled, full, or simple mode.
- Full mode uses backref walks and dirty extent accounting to maintain referenced/exclusive counters.
- Simple mode uses simpler per-owner deltas and `SIMPLE_QUOTA` enable generation tracking.
- `btrfs_qgroup_enabled()` and `btrfs_qgroup_full_accounting()` are convenience predicates used throughout the file.

In-memory model:
- `fs_info->qgroup_tree` stores `struct btrfs_qgroup` nodes in an rb-tree keyed by qgroupid.
- Each qgroup tracks referenced/exclusive bytes and compressed variants, limit fields, reservation buckets, parent/member relation lists, dirty status, iterator list nodes, temporary refcount fields, and sysfs kobject state.
- Relations are represented by `struct btrfs_qgroup_list` and linked from both member and parent.
- Reservation buckets distinguish data, metadata per-transaction, and metadata preallocation.

Configuration loading and cleanup:
- `btrfs_read_qgroup_config()` reads the quota tree at mount:
  - pass 1 reads status, qgroup info, and qgroup limits.
  - pass 2 reads relation items.
  - it initializes sysfs entries, sets quota-enabled state, resumes queued rescan when needed, and marks full qgroups inconsistent on generation/config mismatches.
- `btrfs_free_qgroup_config()` frees rb-tree entries, relation lists, and sysfs state.
- `btrfs_check_quota_leak()` reports unreleased qgroup reservations at unmount.

Quota enable/disable:
- `btrfs_quota_enable()` creates the quota tree and status item, adds qgroups for existing subvolumes and the default filesystem tree, sets simple/full mode flags, commits the setup transaction, then starts a rescan for full qgroups.
- Simple quota enable sets the incompat feature and records `qgroup_enable_gen` for later delta filtering.
- `btrfs_quota_disable()` stops rescan, flushes outstanding reservations through delalloc/ordered extents/commit, removes the quota root from `fs_info`, frees qgroup config, cleans the quota tree, deletes the root, and frees the root block.

On-disk item helpers:
- `add_qgroup_item()` creates info and limit items for a qgroup.
- `del_qgroup_item()` removes both info and limit items.
- `add_qgroup_relation_item()` and `del_qgroup_relation_item()` maintain mirrored relation items.
- `update_qgroup_info_item()`, `update_qgroup_limit_item()`, and `update_qgroup_status_item()` persist dirty in-memory state to the quota tree.

Qgroup hierarchy operations:
- `btrfs_add_qgroup_relation()` validates qgroup levels, inserts mirrored relation items, links the in-memory relation, and attempts quick accounting if the child is fully exclusive.
- `btrfs_del_qgroup_relation()` removes mirrored relation items and updates in-memory accounting.
- `btrfs_create_qgroup()` creates the on-disk items, in-memory qgroup, and sysfs entry.
- `btrfs_remove_qgroup()` enforces deletion rules:
  - parent qgroups must have no children.
  - level-0 qgroups cannot be removed while the subvolume root still exists.
  - simple quota level-0 qgroups must have no remaining usage because shared extents can outlive deleted subvolumes.
- `btrfs_qgroup_cleanup_dropped_subvolume()` commits current accounting, tries to remove the dropped subvolume qgroup, and ignores expected busy/missing cases.
- `btrfs_limit_qgroup()` updates limit fields, supports `-1` as a clear value, and writes the limit item.

Dirty extent tracing and full accounting:
- Dirty extents are tracked in `trans->transaction->delayed_refs.dirty_extents`, an xarray keyed by `bytenr >> sectorsize_bits`.
- `btrfs_qgroup_trace_extent_nolock()` inserts a preallocated extent record while holding the xarray lock, merging data reservation info into an existing record when needed.
- `btrfs_qgroup_trace_extent_post()` walks commit-root backrefs to populate `old_roots` outside spinlock context.
- `btrfs_qgroup_trace_extent()` is the allocating wrapper.
- `btrfs_qgroup_trace_leaf_items()` traces non-inline file extent items in a leaf.
- `btrfs_qgroup_trace_subtree()` traces metadata and data extents under a subtree, but can mark qgroups inconsistent if the subtree level exceeds the configured threshold.

Accounting update:
- `btrfs_qgroup_account_extents()` runs during transaction commit. For each dirty extent, it finds current roots, optionally removes `qgroup_to_skip`, calls `btrfs_qgroup_account_extent()`, frees any recorded data reservation, removes the xarray entry, and frees the record.
- `btrfs_qgroup_account_extent()` compares old and new root sets, skips non-filesystem roots, respects rescan progress, updates qgroup refcounts, updates referenced/exclusive counters, advances `qgroup_seq`, and frees ulist inputs.
- `qgroup_update_counters()` implements the referenced/exclusive transition matrix for none/shared/exclusive states.
- `btrfs_run_qgroups()` writes dirty qgroups and status state to disk.

Snapshot/inherit behavior:
- `btrfs_qgroup_check_inherit()` validates ioctl inheritance structures and rejects deprecated direct ref/excl copy counts.
- `qgroup_auto_inherit()` creates an inherit structure from the parent qgroups of the inode root for simple quotas.
- `qgroup_snapshot_quick_inherit()` handles a narrow full-accounting fast path when the source has one matching parent that exclusively owns its bytes.
- `btrfs_qgroup_inherit()` creates the new qgroup, inserts inherited relations, copies limits/accounting when appropriate, and marks full qgroups inconsistent when a rescan is needed.

Rescan:
- `qgroup_rescan_init()` initializes rescan state, rejects simple mode, handles mount-time resume vs ioctl-initiated rescan, clears runtime cancel/no-accounting flags, and initializes the rescan work item.
- `btrfs_qgroup_rescan()` initializes rescan, commits current work, zeros current qgroup counters, and queues the worker.
- `btrfs_qgroup_rescan_worker()` repeatedly starts transactions and calls `qgroup_rescan_leaf()` until done, stopped, or failed; it updates status flags and completes waiters.
- `qgroup_rescan_leaf()` walks extent tree leaves from `qgroup_rescan_progress`, clones the leaf, walks extent and metadata items, finds all roots, and accounts each extent as newly referenced.
- `btrfs_qgroup_wait_for_completion()` waits for an active rescan.
- `btrfs_qgroup_rescan_resume()` queues a saved rescan during mount.

Reservation APIs:
- `btrfs_qgroup_reserve_data()` sets `EXTENT_QGROUP_RESERVED` over an inode range, tracks newly reserved bytes with `extent_changeset`, enforces qgroup limits, and retries after `try_flush_qgroup()` on quota exhaustion.
- `btrfs_qgroup_free_data()` clears reserved ranges and frees qgroup data reservation.
- `btrfs_qgroup_release_data()` clears the inode io_tree reservation only after data reaches disk; accounting frees qgroup reservation later at commit.
- `btrfs_qgroup_reserve_meta_prealloc()` reserves metadata prealloc bytes and can retry after flush.
- `btrfs_qgroup_free_meta_prealloc()`, `btrfs_qgroup_free_meta_all_pertrans()`, and `btrfs_qgroup_convert_reserved_meta()` maintain metadata reservation buckets.
- `btrfs_qgroup_check_reserved_leak()` clears and reports leaked inode data reservations.

Relocation and swapped subtree tracking:
- `btrfs_qgroup_init_swapped_blocks()` initializes per-root swapped block rb-trees.
- `btrfs_qgroup_add_swapped_blocks()` records subtree roots involved in balance/relocation swaps so expensive subtree tracing can be delayed.
- `btrfs_qgroup_trace_subtree_after_cow()` checks whether a COWed block matches a recorded swapped subtree, removes the record, reads the reloc counterpart, and traces both subtrees.
- `btrfs_qgroup_clean_swapped_blocks()` frees remaining delayed records at transaction commit.
- `qgroup_trace_subtree_swap()` and helpers walk generation-aware reloc subtrees and trace corresponding source/destination blocks.

Simple quota delta path:
- `btrfs_record_squota_delta()` applies simple quota increments/decrements for a filesystem root when the delta generation is at or after `qgroup_enable_gen`.
- It updates both `excl` and `rfer` equally through parent qgroups and marks touched qgroups dirty.

Error and consistency strategy:
- Full accounting marks qgroups inconsistent and can set runtime no-accounting/cancel-rescan when exact accounting is unsafe or too expensive.
- Many paths prefer preserving filesystem operation progress while forcing later rescan rather than aborting for recoverable accounting uncertainty.
- The file is lock-order sensitive: transaction start/commit, `qgroup_ioctl_lock`, `qgroup_lock`, `qgroup_rescan_lock`, and fs freeze interactions are explicitly managed.
