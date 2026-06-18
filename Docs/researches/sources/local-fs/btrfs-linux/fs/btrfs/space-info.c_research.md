# File Research: sources/local-fs/btrfs-linux/fs/btrfs/space-info.c

This file implements Btrfs space-info initialization, logical/disk byte accounting, metadata/data reservation tickets, ENOSPC reclaim state machines, preemptive metadata flushing, zoned reclaim/reset integration, and periodic block group reclaim policy.

Core responsibilities:
- Create `struct btrfs_space_info` objects for SYSTEM, METADATA, DATA, mixed DATA+METADATA, and optional METADATA_REMAP spaces.
- Maintain aggregate counters when block groups are attached: logical total/used/reserved/may-use/pinned/readonly/zone-unusable and mirrored disk totals.
- Decide when metadata reservations may overcommit unallocated chunk space.
- Queue reservation tickets when immediate reservation is impossible, then grant or fail them as reclaim makes progress.
- Run normal async reclaim, priority reclaim, data reclaim, and preemptive metadata reclaim.
- Compute automatic block group reclaim thresholds and schedule reclaim sweeps.

Initialization and space lookup:
- `calc_chunk_size()` chooses default chunk size: zone size for zoned filesystems, 1G or 256M metadata chunks depending on filesystem size, 32M system/remap chunks, and max-sized data chunks.
- `init_space_info()` initializes locks, block-group lists, ticket lists, sysfs-visible defaults, chunk size, subgroup id, and zoned reclaim threshold.
- `create_space_info()` allocates the primary space info, creates zoned subgroups for data relocation or tree-log metadata where needed, adds sysfs nodes, links the object into `fs_info->space_info`, and records `fs_info->data_sinfo`.
- `btrfs_init_space_info()` creates the set of space infos according to superblock incompat features such as mixed block groups and remap tree.
- `btrfs_find_space_info()` matches requested block-group type flags against the mounted filesystem's space-info list.
- `btrfs_clear_space_info_full()` clears `full` after adding capacity.

Reservation ticket model:
- `struct reserve_ticket` carries requested bytes, error, global-reserve-steal permission, list node, waitqueue, and a private lock.
- `reserve_bytes()` is the central reservation path used by metadata and data reservations.
- Immediate success adds bytes to `bytes_may_use` when current used space plus request fits total bytes or, for metadata only, `can_overcommit()` allows it.
- `BTRFS_RESERVE_FLUSH_EMERGENCY` ignores `bytes_may_use` when necessary and fits only against real allocated space.
- Normal flushers append to `space_info->tickets` and queue async reclaim work; priority flushers append to `priority_tickets` and perform their own limited reclaim.
- `remove_ticket()` removes a ticket from its list, adjusts `reclaim_size`, sets success or error state, and wakes waiters.
- `btrfs_try_granting_tickets()` grants priority tickets before normal tickets and updates `tickets_id` whenever a ticket is satisfied.
- `wait_reserve_ticket()` handles fatal-signal interruption by removing the ticket under `space_info->lock` to avoid leaking reserved `bytes_may_use`.
- `handle_reserve_ticket()` selects wait, priority metadata reclaim, priority data reclaim, or evict-style reclaim according to `enum btrfs_reserve_flush_enum`.

Overcommit and free-space calculation:
- `calc_effective_data_chunk_size()` derives the conservative data chunk size used to protect metadata overcommit from immediate data consumption.
- `calc_available_free_space()` estimates unallocated space available to metadata/system chunks, honoring per-profile availability when available, mirroring factors, data chunk reservation headroom, flush aggressiveness, and zone-size alignment on zoned filesystems.
- `check_can_overcommit()` tests whether allocated used bytes plus requested bytes fit allocated bytes plus computed unallocated allowance.
- `can_overcommit()` and `btrfs_can_overcommit()` reject overcommit for DATA or mixed DATA+METADATA space and only apply the logic to metadata/system-style reservations.

Flush state machine:
- `flush_space()` dispatches individual `enum btrfs_flush_state` actions:
  - delayed inode items with bounded or full count,
  - delalloc flushing and ordered-extent waiting,
  - delayed refs with bounded or full count,
  - normal or forced chunk allocation,
  - zoned block group reclaim or unused-zone reset,
  - delayed iputs,
  - current transaction commit.
- `shrink_delalloc()` starts delalloc writeback, waits for async delalloc submission to catch up, optionally waits for ordered extents, and loops while tickets still need space.
- `btrfs_calc_reclaim_metadata_size()` uses `reclaim_size`, current used bytes, and available overcommit room to decide how much metadata pressure to apply.
- `do_async_reclaim_metadata_space()` walks the metadata flush sequence, skips full delalloc and forced chunk allocation on the first cycle to avoid over-flushing/underutilized chunks, commits or resets zones at the end, and fails tickets after repeated nonprogress.
- `do_async_reclaim_data_space()` first tries forced data chunk allocation until the space info is full, then cycles through data-specific states: full delalloc, delayed iputs, transaction commit, zoned reclaim/reset, and forced chunk allocation.
- `btrfs_async_reclaim_metadata_space()` and `btrfs_async_reclaim_data_space()` run primary space infos and their zoned subgroups.

Priority and preemptive reclaim:
- `priority_flush_states` perform delayed item flushing, zone reset, and chunk allocation for limited high-priority metadata reservations.
- `evict_flush_states` are broader and include delayed refs, delalloc, chunk allocation, transaction commit, and zone reset.
- `priority_reclaim_metadata_space()` flushes the configured state list, then either fails the ticket, steals from global reserve when allowed, or returns filesystem abort errors.
- `priority_reclaim_data_space()` tries forced chunk allocation until the data space info is marked full, then fails the ticket.
- `need_preemptive_reclaim()` determines whether background metadata reclaim should start before writers block on tickets, considering global reserve, fullness, bytes pinned/may-use, ordered vs delalloc balance, and a dynamic `clamp` divisor.
- `btrfs_preempt_reclaim_metadata_space()` picks the largest reclaimable source among delalloc, pinned bytes, delayed items, and delayed refs, reclaims one quarter of that pressure, and adjusts the clamp if only one loop was needed.
- `maybe_clamp_preempt()` tightens preemptive reclaim thresholds when queued tickets prove background reclaim is falling behind buffered writers.

Ticket failure and global reserve:
- `steal_from_global_rsv()` can satisfy selected tickets from the global block reserve if the reserve belongs to the same space info and retains at least 10% of its target size.
- `maybe_fail_all_tickets()` runs when reclaim made no progress after repeated cycles. It can fail tickets with `-ENOSPC` or filesystem abort error, tries global-reserve stealing, and re-runs ticket granting so smaller later tickets can still proceed.
- `btrfs_dump_space_info()` and `btrfs_dump_space_info_for_trans_abort()` provide ENOSPC diagnostics for space infos, global block reserves, block groups, and free-space cache state.

Block group reclaim:
- `btrfs_account_ro_block_groups_free_space()` reports unused space inside readonly block groups, including RAID mirror factors, for `statfs`.
- `calc_unalloc_target()` targets ten effective data chunks of unallocated space.
- `calc_dynamic_reclaim_threshold()` raises reclaim intensity as unallocated chunk space falls below that target and backs off when the space info lacks enough unused allocated space to relocate.
- `btrfs_calc_reclaim_threshold()` selects either dynamic threshold or fixed `bg_reclaim_threshold`.
- `is_reclaim_urgent()` treats the filesystem as urgent when unallocated space is less than one effective data chunk.
- `do_reclaim_sweep()` scans block groups by RAID profile, marks groups below threshold that have aged at least one pass, and in urgent mode may do a second pass that accepts fresh candidates.
- `btrfs_reclaim_sweep()` runs periodic reclaim for eligible non-system space infos.
- `btrfs_space_info_update_reclaimable()` and `btrfs_set_periodic_reclaim_ready()` track net reclaimable bytes and arm/disarm cleaner-thread reclaim.

Cross-file relationships:
- `space-info.h` declares the structures, flush enums, counter helpers, and exported API implemented here.
- `block-group.c`, `extent-tree.c`, `delalloc-space.c`, `transaction.c`, and allocator paths update space-info counters and call reservation helpers.
- `super.c` uses `btrfs_account_ro_block_groups_free_space()` for `statfs` and cancels async reclaim work during readonly remount.
- `sysfs.c` exposes space-info objects and reclaim counters.
- `zoned.c` supplies reclaim, reset, and zoned-mode policy used by the flush states and subgroup setup.
- `free-space-cache.c` is used for diagnostic dumping of per-block-group free space.

Important invariants and risks:
- `space_info->lock` protects byte counters, ticket lists, `reclaim_size`, `tickets_id`, and reclaim-ready state.
- `groups_sem` protects block-group list traversal and insertion.
- Metadata overcommit must reserve one effective data chunk of unallocated space so data allocation cannot consume all metadata headroom.
- Normal reservation flush modes that can commit transactions are forbidden when `current->journal_info` is set.
- Ticket grant order is priority tickets first, then normal tickets; skipped or interrupted tickets must be removed before they can be granted.
- `bytes_may_use` is the reservation handoff point: reservations add it, extent allocation moves it to `bytes_reserved`, and block-group updates move reserved bytes to used bytes.
- Zoned mode changes several endpoints: chunk size is zone size, available overcommit is zone-aligned, data/metadata subgroups exist, and final reclaim may reset zones rather than only committing transactions.
