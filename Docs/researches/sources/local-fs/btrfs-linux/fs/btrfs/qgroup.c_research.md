# File Research: sources/local-fs/btrfs-linux/fs/btrfs/qgroup.c

This file implements Btrfs quota groups, including full qgroup accounting, simple quota accounting, qgroup configuration loading, qgroup relation management, quota enable/disable, rescan workers, reservation enforcement, delayed extent accounting, and relocation swap handling.

Modes and global state:
- `btrfs_qgroup_mode()` returns disabled, full, or simple mode from fs flags and qgroup status flags.
- `btrfs_qgroup_enabled()` and `btrfs_qgroup_full_accounting()` are mode predicates.
- Full accounting tracks referenced/exclusive bytes through backref walks.
- Simple quota mode tracks ownership deltas against root ownership and propagates through qgroup parents.

In-memory qgroup management:
- Qgroups are stored in `fs_info->qgroup_tree`, an rb-tree keyed by qgroup ID.
- `find_qgroup_rb()`, `add_qgroup_rb()`, `del_qgroup_rb()`, and relation helpers manage qgroup and parent/member graph state.
- `qgroup_dirty()` adds changed qgroups to `fs_info->dirty_qgroups` for later disk updates.
- Iterator lists prevent duplicate traversal while propagating updates through parent qgroups.

On-disk config loading and writing:
- `btrfs_read_qgroup_config()` reads the quota tree during mount:
  - pass 1 reads status, info, and limit items;
  - pass 2 reads bidirectional qgroup relation items;
  - inconsistent generation/config marks full qgroups inconsistent;
  - simple mode reads `qgroup_enable_gen`.
- `add_qgroup_item()`, `del_qgroup_item()`, `update_qgroup_info_item()`, `update_qgroup_limit_item()`, and `update_qgroup_status_item()` maintain quota-tree items.
- `btrfs_run_qgroups()` writes dirty qgroup info/limit items and updates the status item during transaction commit or qgroup assignment.

Quota enable/disable:
- `btrfs_quota_enable()` creates the quota tree, status item, qgroup records for existing roots, and the fs tree qgroup.
- Full mode starts inconsistent and queues a rescan; simple mode sets the simple-quota incompat flag and an enable generation.
- `btrfs_quota_disable()` stops rescans, flushes outstanding reservations, clears quota state, deletes quota-tree contents, deletes the quota root, and frees config.
- `flush_reservations()` drains delalloc, ordered extents, and commits so stale qgroup reservations do not reappear after re-enable.

Qgroup relation and lifecycle operations:
- `btrfs_add_qgroup_relation()` validates levels, creates both relation items, adds the in-memory relation, and attempts quick accounting propagation.
- `btrfs_del_qgroup_relation()` removes both relation directions and updates accounting if possible.
- `btrfs_create_qgroup()` creates a new qgroup item and sysfs entry.
- `btrfs_remove_qgroup()` verifies deletability, removes relation/item state, warns on non-zero reservations, and marks full qgroups inconsistent if non-zero usage is being deleted.
- `btrfs_qgroup_cleanup_dropped_subvolume()` removes a dropped subvolume’s qgroup after committing current accounting, ignoring expected busy/absent cases.
- `btrfs_limit_qgroup()` updates max referenced/exclusive and reservation limits, with `-1` used as a clear sentinel.

Delayed extent tracing and full accounting:
- `btrfs_qgroup_trace_extent_nolock()` records dirty extents in delayed refs’ xarray by sectorsize-shifted bytenr.
- `btrfs_qgroup_trace_extent_post()` populates old roots using commit-root backref walks after dropping spinlock context.
- `btrfs_qgroup_trace_extent()` wraps allocation, xarray reservation, insert, and post-processing.
- `btrfs_qgroup_trace_leaf_items()` scans file extent items in a leaf and traces non-inline disk-backed extents.
- `btrfs_qgroup_account_extents()` walks dirty extent records at commit time, computes new roots, optionally skips one qgroup, calls `btrfs_qgroup_account_extent()`, frees associated data reservations, and erases records.
- `btrfs_qgroup_account_extent()` compares old/new root sets, filters non-fstree roots, coordinates with rescan progress, updates refcounts and counters, and frees root ulist resources.

Counter logic:
- `qgroup_update_refcnt()` walks root qgroups and parents, accumulating old or new reference counts under a sequence number.
- `qgroup_update_counters()` updates referenced and exclusive byte counters based on old/new refcount transitions.
- `quick_update_accounting()` handles relation changes cheaply when child referenced bytes are entirely exclusive; otherwise it marks full qgroups inconsistent.
- `btrfs_record_squota_delta()` handles simple quota byte deltas, skips extents older than the simple-quota enable generation, propagates to parent qgroups, and guards against underflow.

Snapshot/subvolume inheritance:
- `btrfs_qgroup_check_inherit()` validates inherit payload size, flags, and referenced parent qgroups; old ref/excl copy behavior is rejected.
- `qgroup_auto_inherit()` derives simple-quota inherited parents from the containing root’s parent qgroups.
- `qgroup_snapshot_quick_inherit()` can avoid a rescan when a snapshot parent relationship is simple enough to update by nodesize.
- `btrfs_qgroup_inherit()` creates the destination qgroup, adds inherited relations, copies selected limits/accounting from the source, and marks inconsistent if manual or unsafe inheritance needs rescan.

Rescan:
- `qgroup_rescan_init()` validates state, sets rescan flags/progress, clears runtime cancel/no-accounting flags, and initializes work.
- `qgroup_rescan_zero_tracking()` clears all current qgroup rfer/excl counters and marks qgroups dirty.
- `btrfs_qgroup_rescan()` commits current work, zeros tracking, and queues the worker for full accounting.
- `qgroup_rescan_leaf()` scans extent-tree leaves from progress, clones a scratch leaf, walks extent/metadata items, finds all roots, and accounts them as new roots.
- `btrfs_qgroup_rescan_worker()` repeatedly scans leaves in transactions, updates inconsistent/rescan flags, completes waiters, and logs paused/cancelled/completed/failed outcomes.
- `btrfs_qgroup_wait_for_completion()` waits for the rescan completion, optionally interruptibly.
- `btrfs_qgroup_rescan_resume()` queues an interrupted mount-time rescan.

Reservation enforcement:
- `qgroup_reserve()` checks limits across a root qgroup and its parents, honoring quota override for capable users, then records reservations.
- `btrfs_qgroup_free_refroot()` releases reservations for a root and all parent qgroups; `(u64)-1` frees all per-transaction metadata reservation.
- `btrfs_qgroup_reserve_data()` reserves data ranges by setting `EXTENT_QGROUP_RESERVED`, enforcing limits, and retrying after flushing qgroup space on `-EDQUOT`.
- `btrfs_qgroup_free_data()` clears reserved ranges and frees qgroup data reservation.
- `btrfs_qgroup_release_data()` clears the io-tree reservation bit without freeing qgroup bytes, for data that reached disk and will be accounted at commit.
- Metadata APIs reserve, free, and convert prealloc/per-transaction metadata reservations, mirrored in root-local reservation counters to avoid underflow across quota mode transitions.
- `try_flush_qgroup()` flushes delalloc, waits ordered extents, runs delayed iputs, and commits to recover qgroup space.

Relocation swapped-block accounting:
- `btrfs_qgroup_init_swapped_blocks()` initializes per-level rb-trees used to remember swapped subtree roots.
- `btrfs_qgroup_add_swapped_blocks()` records subvolume/reloc subtree roots before balance swaps them, including level, generations, first key, last snapshot, and whether leaves need tracing.
- `btrfs_qgroup_trace_subtree_after_cow()` detects later COW of a swapped subtree root, removes the record, reads the reloc counterpart, and traces both subtrees.
- `qgroup_trace_subtree_swap()` and helpers do generation-aware traversal so only new relocation blocks and corresponding subvolume blocks are traced.
- `btrfs_qgroup_clean_swapped_blocks()` drops remaining swap records at transaction commit when no delayed trace was needed.

Cleanup and diagnostics:
- `btrfs_check_quota_leak()` reports unreleased qgroup reservations at unmount.
- `btrfs_free_qgroup_config()` frees in-memory qgroup trees and sysfs state.
- `btrfs_qgroup_check_reserved_leak()` clears and reports leaked inode data reservation bits at inode destruction.
- `btrfs_qgroup_destroy_extent_records()` frees delayed-ref dirty extent records and destroys the xarray.

Concurrency:
- `qgroup_ioctl_lock` serializes ioctl/config operations.
- `qgroup_lock` protects in-memory qgroup rb-tree/list/counter state.
- `qgroup_rescan_lock` protects rescan state and progress.
- The code deliberately drops locks before starting/committing transactions in several paths to avoid lock inversions with freeze, rescan, and qgroup ioctl paths.
