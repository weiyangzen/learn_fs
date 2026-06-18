# File Research: sources/os/linux/linux-stable/fs/btrfs/space-info.c

This file implements Btrfs space accounting, reservation admission, ENOSPC ticketing, async reclaim, preemptive metadata reclaim, and block-group reclaim threshold logic.

Key responsibilities:
- Initializes `btrfs_space_info` objects for SYSTEM, METADATA, DATA, mixed DATA+METADATA, and metadata remap profiles via `btrfs_init_space_info()`.
- Creates zoned-mode subgroups for data relocation and tree-log space with sysfs entries.
- Accounts block groups into a space-info through `btrfs_add_bg_to_space_info()`, updating logical totals, disk totals, used bytes, readonly bytes, superblock reservation bytes, and zone-unusable bytes.
- Provides lookup and state clearing helpers: `btrfs_find_space_info()` and `btrfs_clear_space_info_full()`.

Reservation model:
- `reserve_bytes()` is the central allocator admission path for both metadata and data reservations.
- Fast path grants reservations by increasing `bytes_may_use` if current usage plus requested bytes fits `total_bytes`, or if metadata overcommit is allowed.
- Metadata overcommit is deliberately disabled for data and mixed block group space.
- `BTRFS_RESERVE_FLUSH_EMERGENCY` bypasses normal `bytes_may_use` accounting pressure and admits only if actual non-`may_use` space can fit the request.
- Public wrappers are `btrfs_reserve_metadata_bytes()` and `btrfs_reserve_data_bytes()`.

Ticketing and ENOSPC handling:
- Failed reservations may create a stack-local `reserve_ticket` and enqueue it on `priority_tickets` or normal `tickets`.
- `btrfs_try_granting_tickets()` grants priority tickets before normal tickets, maintaining `reclaim_size` and `tickets_id`.
- `remove_ticket()` handles list removal, error assignment, successful completion, and wakeups.
- Normal waiters use `wait_reserve_ticket()` with killable waits; interrupted waits remove their own ticket to avoid leaked `bytes_may_use`.
- `maybe_fail_all_tickets()` fails tickets after reclaim has exhausted useful progress, optionally stealing from the global block reserve for allowed flush modes.

Flush and reclaim machinery:
- `flush_space()` maps `enum btrfs_flush_state` to concrete reclaim actions:
  - delayed inode item flushing,
  - delayed ref running,
  - delalloc writeout and ordered extent waiting,
  - chunk allocation,
  - delayed iputs,
  - transaction commit,
  - zoned block-group reclaim,
  - zoned reset of unused block groups.
- Metadata async reclaim starts at delayed items and advances through increasingly expensive states until tickets are satisfied or failed.
- Data async reclaim first tries forced chunk allocation while the space-info is not full, then runs full delalloc, delayed iputs, transaction commit, zoned reclaim/reset, and forced chunk allocation.
- Priority reclaim paths perform bounded synchronous flushing for callers that cannot wait on the normal async worker.

Preemptive reclaim:
- `need_preemptive_reclaim()` decides whether background metadata flushing should start before callers block on tickets.
- It avoids competing with active ticket reclaim, avoids running when the fs is closing or remounting, accounts for the global reserve, and scales aggressiveness through `space_info->clamp`.
- `btrfs_preempt_reclaim_metadata_space()` chooses what to flush based on the dominant reclaimable pool: delalloc, pinned bytes, delayed items, or delayed refs.

Chunk/free-space calculations:
- `calc_chunk_size()` chooses default chunk sizes based on zoned mode, block group type, total writable bytes, and metadata/data/system profile.
- `calc_effective_data_chunk_size()` bounds data chunk assumptions to 10% of writable device space or 1 GiB, except zoned mode where zone size is used directly.
- `calc_available_free_space()` estimates metadata overcommit capacity from unallocated chunk space or per-profile availability and reserves headroom for future data chunks.

Block-group reclaim:
- Dynamic reclaim tries to protect unallocated space by comparing free chunk space to a target of ten effective data chunks.
- `btrfs_calc_reclaim_threshold()` chooses either dynamic threshold or configured `bg_reclaim_threshold`.
- `btrfs_reclaim_sweep()` scans non-system space-infos and marks underused block groups for reclaim when periodic reclaim is ready.
- `btrfs_space_info_update_reclaimable()` sets periodic reclaim readiness after enough net reclaimable bytes accumulate.
- Urgent reclaim allows fresh block groups to be considered when unallocated space is below one effective data chunk.

Diagnostics and accounting helpers:
- `btrfs_dump_space_info()` prints aggregate space-info state, global block reserves, per-block-group availability, and free-space details.
- `btrfs_dump_space_info_for_trans_abort()` dumps all space-infos during transaction abort diagnostics.
- `btrfs_account_ro_block_groups_free_space()` reports unused readonly block group space for `df`-style accounting.
- `btrfs_return_free_space()` first refills the global reserve when possible, then grants pending tickets.

Concurrency and invariants:
- `space_info->lock` protects byte counters, ticket lists, reclaim flags, and reclaim counters.
- `groups_sem` protects block-group lists by RAID index.
- Ticket internals use their own spinlock and waitqueue.
- Reservation code asserts that transaction-holding callers do not use flush modes that can commit transactions and deadlock.
- The implementation relies on monotonic `tickets_id` to detect progress across reclaim cycles.
