# File Research: sources/local-fs/kdave-linux/fs/btrfs/space-info.c

Read coverage: complete file, 2258 lines.

This file implements Btrfs space reservation, ENOSPC ticketing, async reclaim, preemptive metadata reclaim, data-space reclaim, and periodic block-group reclaim. It is the implementation backing `space-info.h`.

Main responsibilities:
- Initializes `btrfs_space_info` instances for system, metadata, data, mixed data+metadata, and remap-tree block-group classes.
- Tracks block-group totals, used bytes, disk totals, readonly bytes, zone-unusable bytes, and reclaim state.
- Implements metadata overcommit policy with `calc_available_free_space()`, `btrfs_can_overcommit()`, and reserve-time checks.
- Implements reservation tickets with FIFO-style normal tickets and separate priority tickets.
- Drives flushing through ordered states: delayed items, delayed refs, delalloc, chunk allocation, delayed iputs, transaction commit, zoned reset, and zoned reclaim.
- Exposes diagnostics through `btrfs_dump_space_info()` and transaction-abort dump helpers.
- Implements dynamic and periodic block-group reclaim thresholds.

Important flows:
- `btrfs_init_space_info()` creates initial space-info objects based on superblock incompat features.
- `btrfs_add_bg_to_space_info()` accounts a block group into its space info and links it by RAID index.
- `reserve_bytes()` is the central reservation engine. It checks current usage, pending tickets, overcommit eligibility, emergency reservation rules, ticket creation, async work triggering, and preemptive reclaim triggering.
- `btrfs_reserve_metadata_bytes()` and `btrfs_reserve_data_bytes()` are the public metadata/data entry points.
- `btrfs_try_granting_tickets()` grants priority tickets first, then normal tickets, updating `bytes_may_use`.
- `do_async_reclaim_metadata_space()` advances the metadata reclaim state machine until tickets are served or failed.
- `do_async_reclaim_data_space()` tries forced data chunk allocation, then escalates through data reclaim states.
- `btrfs_reclaim_sweep()` scans reclaim-ready space infos and marks low-utilization block groups for relocation.

Concurrency and invariants:
- `space_info->lock` protects core counters, ticket lists, reclaim flags, and reclaim threshold state.
- `groups_sem` protects block-group list traversal and mutation.
- Ticket wait state has its own spinlock and waitqueue.
- Reservation paths assert that transaction-holding callers do not use flush modes that may commit and deadlock.
- Counter update helpers from the header trace changes and guard underflow.

Integration points:
- Uses transaction, delayed inode, delayed ref, ordered extent, chunk allocator, block-group, zoned, free-space-cache, and sysfs subsystems.
- Work items initialized by `btrfs_init_async_reclaim_work()` are stored in `btrfs_fs_info`.
- `super.c` consumes readonly block-group accounting through `btrfs_account_ro_block_groups_free_space()` for `statfs`.

Risk notes:
- Reservation correctness depends on strict lock ordering and ticket removal semantics; interrupted waits explicitly remove tickets to avoid `bytes_may_use` leaks.
- Metadata overcommit is intentionally conservative and disabled for mixed/data space infos.
- Zoned mode changes reclaim termination and chunk sizing; regressions here can surface as false ENOSPC or overcommit.
- Dynamic reclaim threshold math intentionally uses approximations and overflow-aware percentage calculation.
