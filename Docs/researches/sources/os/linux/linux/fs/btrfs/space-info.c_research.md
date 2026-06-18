# File Research: sources/os/linux/linux/fs/btrfs/space-info.c

## Scope And Role

`space-info.c` implements Btrfs logical space accounting, reservation admission, ENOSPC ticketing, async reclaim, preemptive metadata reclaim, data reclaim, zoned reclaim hooks, and periodic block-group reclaim policy.

The file is the core bridge between high-level reservations and lower-level block group/chunk allocation. It manages `struct btrfs_space_info` instances for system, metadata, data, mixed data+metadata, and remap-tree space types, and it coordinates reclaim by running delayed items, delayed refs, delalloc writeback, ordered extent waits, delayed iputs, transaction commits, chunk allocation, zone reset, and zone reclaim.

A long introductory comment describes the reservation model:

- `space_info` is the arbiter for total usable logical space.
- `block_rsv` objects are reservation buckets accounted mostly through `bytes_may_use`.
- Reservation helpers charge `bytes_may_use`, then allocation and extent insertion move bytes through `bytes_reserved` and `bytes_used`.
- When immediate reservation fails, requesters create tickets and either wait for async reclaim or run priority reclaim inline.
- Metadata can overcommit against unallocated chunk space; data reservations do not overcommit.

## Main Data Structures

`struct reserve_ticket` is the per-waiter reservation object:

- `bytes`: remaining requested bytes.
- `error`: failure code, commonly `-ENOSPC`, `-EINTR`, or filesystem abort error.
- `steal`: whether the ticket may steal from the global reserve.
- `list`: links into `space_info->tickets` or `space_info->priority_tickets`.
- `wait`: wait queue for normal ticket waiters.
- `lock`: protects ticket state during wakeups and interruption.

`struct btrfs_space_info` is defined in `space-info.h`; this file initializes and mutates its counters, ticket lists, block-group lists, reclaim flags, and sysfs-visible reclaim counters.

## Space Info Creation And Initialization

`calc_chunk_size()` chooses default chunk size:

- Zoned filesystems use `fs_info->zone_size`.
- Data uses `BTRFS_MAX_DATA_CHUNK_SIZE`.
- System and metadata-remap use `32 MiB`.
- Metadata uses `1 GiB` on filesystems larger than `50 GiB`, otherwise `256 MiB`.

`init_space_info()` initializes block-group lists, locks, ticket lists, reclaim defaults, chunk size, flags, and zoned default reclaim threshold.

`create_space_info()` allocates a primary `btrfs_space_info`, optionally adds a zoned sub-group, registers sysfs entries, links it into `fs_info->space_info`, and stores `fs_info->data_sinfo` for data space.

`create_space_info_sub_group()` creates a child space info for zoned data relocation or treelog accounting. The implementation currently allows one sub-group slot per primary space info.

`btrfs_init_space_info()` creates:

- System space.
- Either mixed data+metadata space or separate metadata and data spaces.
- Metadata-remap space when `BTRFS_FEATURE_INCOMPAT_REMAP_TREE` is enabled.

`btrfs_add_bg_to_space_info()` folds a block group into its space info counters, including total/disk totals, used bytes, readonly super bytes, zone unusable bytes, and block-group list membership by RAID index. It also tries to grant waiting tickets after new capacity is visible.

`btrfs_find_space_info()` searches by masked block-group type flags and returns the first matching space info.

## Reservation Admission

`reserve_bytes()` is the central reservation routine used by both metadata and data wrappers.

The normal fast path checks:

- Current `btrfs_space_info_used(..., true)`.
- Whether pending tickets should block bypass.
- Whether `used + orig_bytes <= total_bytes`.
- For metadata, whether `can_overcommit()` allows the reservation based on unallocated chunk space.

If successful, it increments `bytes_may_use`.

The emergency path, `BTRFS_RESERVE_FLUSH_EMERGENCY`, ignores current `bytes_may_use` and admits only if actual used space plus the request fits in total bytes. This is intentionally dangerous but allowed for internal reservation pessimism failures.

When reservation fails and ticketing is allowed, `reserve_bytes()` creates a stack ticket, increments `space_info->reclaim_size`, and links the ticket into either:

- `space_info->tickets` for normal async reclaim modes.
- `space_info->priority_tickets` for inline priority reclaim modes.

Normal tickets queue either `async_reclaim_work` or `async_data_reclaim_work`. Metadata fast-path successes may also trigger `preempt_reclaim_work` when reservation pressure is high.

`btrfs_reserve_metadata_bytes()` wraps `reserve_bytes()` and emits ENOSPC trace/debug dumps on failure.

`btrfs_reserve_data_bytes()` restricts callers to data-safe flush modes, wraps `reserve_bytes()`, and emits ENOSPC diagnostics.

## Ticket Granting And Failure

`btrfs_try_granting_tickets()` runs under `space_info->lock`. It grants priority tickets first, then normal tickets. A ticket is granted if the requested bytes fit in currently allocated space or, for metadata, can be overcommitted. Granting increments `bytes_may_use`, removes and wakes the ticket, and advances `tickets_id`.

`remove_ticket()` unlinks a ticket, subtracts its remaining bytes from `reclaim_size`, sets error or success, and wakes waiters.

`wait_reserve_ticket()` waits killably for normal tickets. On fatal signal it removes the ticket while holding `space_info->lock` to avoid leaking a later granted `bytes_may_use` reservation.

`handle_reserve_ticket()` dispatches by flush mode:

- Normal metadata/data flushing waits for async reclaim.
- `BTRFS_RESERVE_FLUSH_LIMIT` and `BTRFS_RESERVE_FLUSH_EVICT` run priority metadata reclaim.
- `BTRFS_RESERVE_FLUSH_FREE_SPACE_INODE` runs priority data reclaim.
- It asserts that successful tickets do not also carry errors.

`maybe_fail_all_tickets()` is used after reclaim exhaustion. It repeatedly fails or grants tickets until progress stops, optionally stealing from the global reserve for eligible tickets, and handles transaction-abort error propagation.

`steal_from_global_rsv()` lets selected tickets consume global block reserve bytes if at least 10% of the global reserve remains beyond the requested bytes.

## Overcommit And Available Space Calculation

`calc_effective_data_chunk_size()` estimates a data chunk size for overcommit and reclaim heuristics, using the data space-info chunk size directly on zoned filesystems and otherwise capping to 10% of device writable bytes and `1 GiB`.

`calc_available_free_space()` estimates how much unallocated physical capacity can support metadata overcommit. It:

- Uses per-profile availability if present, otherwise `free_chunk_space`.
- Divides for mirrored/duplicated profiles.
- Reserves one effective data chunk to avoid data allocations consuming all metadata headroom.
- Allows larger overcommit when not using full flush modes.
- Aligns down to zone size on zoned filesystems.

`can_overcommit()` rejects data/mixed data space and delegates to `check_can_overcommit()` for metadata-like spaces.

`btrfs_can_overcommit()` is the exported lock-held check using current `space_info` usage.

## Reclaim State Machine

`flush_space()` maps `enum btrfs_flush_state` to concrete reclaim actions:

- Run delayed items.
- Flush delalloc, with optional ordered-extent waits.
- Run delayed refs.
- Allocate chunks, optionally forced.
- Run zoned reclaim and unused block-group deletion.
- Run delayed iputs.
- Commit current transaction.
- Reset unused zones.

It traces every flush attempt with result and preemptive/normal context.

`shrink_delalloc()` starts delalloc writeback across roots, waits for async compressed delalloc workers to establish ordered extents, optionally waits for ordered extents, and loops up to three times unless doing preemptive one-shot reclaim.

`do_async_reclaim_metadata_space()` is the normal metadata ticket flusher. It progresses through flush states from delayed items through transaction commit or zone reset. It resets to the first state when tickets are granted, skips full delalloc and forced chunk allocation on early cycles, and fails tickets after repeated no-progress commit cycles.

`btrfs_async_reclaim_metadata_space()` runs metadata reclaim for the primary metadata space and any zoned metadata sub-group.

`do_async_reclaim_data_space()` first tries forced chunk allocation until the data space is marked full, then cycles through data states: full delalloc, delayed iputs, transaction commit, zoned reclaim, zone reset, and forced chunk allocation. It fails tickets only when full and no state makes progress.

`btrfs_async_reclaim_data_space()` runs data reclaim for `fs_info->data_sinfo` and its sub-group.

`btrfs_init_async_reclaim_work()` wires the metadata, data, and preemptive reclaim work items.

## Preemptive Metadata Reclaim

`need_preemptive_reclaim()` decides whether background metadata reclaim should run before tasks block on tickets. It avoids reclaim when tickets already exist, the filesystem is effectively full, the pressure is only global reserve, pressure is too small, the filesystem is closing, or remounting is active.

It compares reclaimable pressure against a clamp-scaled threshold based on available metadata headroom. The `clamp` field can tighten thresholds from `1/2` down to `1/256`.

`btrfs_preempt_reclaim_metadata_space()` chooses the dominant reclaim source:

- Delalloc reservations.
- Pinned bytes, via transaction commit.
- Delayed inode block reserve.
- Delayed refs block reserve.

It reclaims one quarter of the selected amount per loop and relaxes `clamp` if one loop was enough.

`maybe_clamp_preempt()` tightens `clamp` when delalloc is growing faster than ordered extents and normal ticketing had to be used.

## Periodic And Dynamic Block-Group Reclaim

`calc_unalloc_target()` sets a target of ten effective data chunks of unallocated space.

`calc_dynamic_reclaim_threshold()` computes a reclaim threshold based on how far unallocated space is below the target, while backing off if there is not enough unused allocated data space to make relocation useful.

`btrfs_calc_reclaim_threshold()` returns either the dynamic threshold or the fixed `bg_reclaim_threshold`.

`is_reclaim_urgent()` treats unallocated space below one effective data chunk as urgent.

`do_reclaim_sweep()` scans block groups for a RAID index, uses the threshold to select underused groups, increments `reclaim_mark`, and calls `btrfs_mark_bg_to_reclaim()` for candidates. Urgent mode can make a second pass to take fresher groups if no stale groups qualified.

`btrfs_space_info_update_reclaimable()` tracks net reclaimable byte changes and marks periodic reclaim ready once at least one data chunk worth of space has become reclaimable.

`btrfs_set_periodic_reclaim_ready()` toggles periodic reclaim readiness and resets accumulated reclaimable bytes when clearing.

`btrfs_reclaim_sweep()` runs periodic reclaim across eligible non-system space infos and all RAID indexes.

## Diagnostics And Stat Helpers

`btrfs_dump_space_info()` logs current counters, global block reserves, block-group counters, free-space details, and aggregate availability.

`btrfs_dump_space_info_for_trans_abort()` logs all space infos and global reserves after ENOSPC-related transaction aborts.

`btrfs_account_ro_block_groups_free_space()` computes unused bytes inside readonly block groups, scaled by RAID factor, for `statfs` accounting.

`btrfs_return_free_space()` preferentially refills the global reserve from returned free space, then tries to grant tickets.

## Concurrency And Locking

`space_info->lock` protects counters, ticket lists, reclaim size, `flush`, `full`, and periodic reclaim fields. Many helpers assert the lock is held.

`groups_sem` protects block-group list traversal and modification.

Ticket state has its own spinlock because waiters and reclaimers race on ticket completion.

Workqueues run async reclaim outside reservation callers, while priority reclaim can run inline for contexts that cannot wait on normal async tickets.

Transaction state is handled carefully: several flush paths use `btrfs_join_transaction_nostart()`, while commit paths assert `current->journal_info == NULL` to avoid deadlock.

## Integration Points

This file depends heavily on:

- `block-group.c` for block-group availability, reclaim marking, chunk allocation, unused group deletion, and zone resets.
- `transaction.c` for delayed refs and commits.
- `ordered-data.c` and delalloc paths for flushing dirty file data.
- `zoned.c` for zone reset/reclaim behavior.
- `sysfs.c` for space-info sysfs registration.
- `super.c` indirectly through mount options such as `ENOSPC_DEBUG` and zoned/free-space settings.

## Risks And Edge Cases

Reservation correctness depends on every counter transition preserving invariants among `bytes_may_use`, `bytes_reserved`, `bytes_used`, `bytes_pinned`, readonly bytes, and zone-unusable bytes.

Ticket interruption is delicate: if a killed task is not removed before reclaim grants it, `bytes_may_use` can leak. `wait_reserve_ticket()` explicitly guards this.

Priority tickets can bypass normal tickets, but only relative to the priority list. Normal no-flush reservations intentionally do not jump existing normal tickets.

Overcommit is intentionally metadata-only; mixed data+metadata profiles are treated as data and cannot overcommit.

Zoned filesystems replace some normal final reclaim states with zone reset/reclaim behavior and require zone-size alignment in available-space calculations.

## Testing Signals

Useful tests should cover:

- Immediate metadata and data reservation success.
- Metadata overcommit with and without unallocated chunk space.
- Ticket queuing, grant ordering, interruption, and ENOSPC failure.
- Priority reclaim modes and global-reserve stealing.
- Async metadata reclaim progress through delayed items, delayed refs, delalloc, chunk allocation, and commit.
- Async data reclaim when data space is full.
- Preemptive reclaim clamp changes under buffered write pressure.
- Zoned reclaim and reset states.
- Periodic reclaim threshold and urgent reclaim behavior.
