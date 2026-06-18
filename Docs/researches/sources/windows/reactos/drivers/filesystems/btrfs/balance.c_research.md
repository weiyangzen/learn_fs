# File Research: sources/windows/reactos/drivers/filesystems/btrfs/balance.c

Implements the WinBtrfs/ReactOS Btrfs balance engine: relocating data and metadata chunks, rewriting extent backreferences, converting allocation profiles, persisting/resuming balance state, pausing/resuming/stopping balance work, and using the same relocation machinery for device removal and shrink flows.

Key entry points:
- `start_balance()` validates a user balance request, checks `SE_MANAGE_VOLUME_PRIVILEGE`, rejects read-only/locked/scrub-active states, records data/metadata/system options, and starts `balance_thread()`.
- `balance_thread()` is the background worker that selects chunks, optionally changes target data/metadata/system profiles, relocates data chunks before metadata/system chunks, handles pause/stop events, persists or removes the on-disk balance item, trims freed device space, and finalizes removal/shrink operations.
- `look_for_balance_item()` loads an interrupted on-disk `BALANCE_ITEM`, applies Linux-style resume heuristics, and restarts the background worker during mount.
- `query_balance()`, `pause_balance()`, `resume_balance()`, and `stop_balance()` implement status/control IOCTL helpers.
- `remove_device()` validates RAID/device-count constraints, marks a target device for relocation, seeds balance options by device id, and starts the balance worker in removal mode.

Metadata relocation:
- `balance_metadata_chunk()` scans extent-tree items inside one metadata/system chunk, collects up to 64 tree blocks per pass, deletes their old extent items, frees their old space, and calls `write_metadata_items()`.
- `add_metadata_reloc()` extracts inline and non-inline `TREE_BLOCK_REF` / `SHARED_BLOCK_REF` records from an extent item and queues a `metadata_reloc`.
- `add_metadata_reloc_parent()` ensures parent tree blocks are also queued so relocated child pointers can be patched.
- `write_metadata_items()` reads old tree blocks, locates or allocates destination metadata space, rewrites parent internal-node addresses, updates root pointers/superblock root addresses when relocating top-level roots, updates loaded tree-cache hash entries, recalculates checksums, writes relocated tree blocks, and recreates their extent items.
- `add_metadata_reloc_extent_item()` rebuilds relocated metadata extent items, splitting excess backrefs into separate extent-tree items when inline backrefs exceed one quarter of node size.

Data relocation:
- `balance_data_chunk()` scans non-tree `EXTENT_ITEM`s in a data chunk, processes at most about 16 MiB or 100 extents per pass, allocates destination data space, copies data in 1 MiB units, moves checksum entries, relocates owning metadata leaves, recreates data extent items, and updates changed-extents lists plus cached file extents.
- `add_data_reloc()` extracts inline and non-inline `EXTENT_DATA_REF` / `SHARED_DATA_REF` records, deletes old extent/backref items, frees old chunk space, and queues data relocation records.
- `data_reloc_add_tree_edr()` finds file extent items referenced by an `EXTENT_DATA_REF`, queues their containing leaf blocks for metadata relocation, and coalesces repeated references from the same tree block.
- `sort_data_reloc_refs()` orders and merges data backrefs before insertion.
- `add_data_reloc_extent_item()` rebuilds relocated data extent items and spills non-inline backrefs when needed.

Balance selection and persistence:
- `get_chunk_dup_type()` extracts a chunk's active RAID/profile flag.
- `should_balance_chunk()` applies enabled-option filters for profile, device id, physical range, virtual range, stripe count, usage percentage, and soft conversion skip.
- `copy_balance_args()` serializes in-memory balance options into an on-disk `BALANCE_ITEM`; `load_balance_args()` deserializes them.
- `add_balance_item()` writes the resumable temp item in the root tree; `remove_balance_item()` deletes it after successful normal balance completion.

Device removal, shrink, and trim support:
- `finish_removing_device()` flushes pending writes, removes device and device-stat items, updates superblock device totals, removes the device from volume/PnP tracking, optionally restores drive-letter mount-manager state, clears on-disk superblocks, frees device-space lists, updates TRIM capability, and notifies volume-size change.
- `remove_superblocks()` zeros known Btrfs superblock locations on a removed writable device.
- `trim_unalloc_space()` computes unallocated physical ranges from the device tree and sends `IOCTL_STORAGE_MANAGE_DATA_SET_ATTRIBUTES` TRIM ranges while avoiding superblock locations.
- `try_consolidation()` frees space by repeatedly relocating the least-used data chunks when a required new chunk cannot be allocated directly.
- `regenerate_space_list()` rebuilds a device's free-space list after failed or canceled shrink work.

Important invariants:
- Tree mutations are performed under `Vcb->tree_lock`; chunk allocation and chunk-list traversal use `Vcb->chunk_lock` and per-chunk locks.
- Relocated metadata must update both on-disk parent pointers and any loaded in-memory `tree`/`tree_data` cache entries.
- Extent refcounts and backrefs must move from old addresses to new addresses without changing logical ownership.
- Data relocation must preserve checksum coverage and explicitly handle no-checksum runs.
- Data chunks are relocated before metadata chunks so metadata rewrites can point at final data addresses.
- On failure, rollback lists restore chunk-space accounting where possible; on success, `do_write()` commits mutations and rollback state is cleared.
- Balance pause/stop is event-driven through `Vcb->balance.event`; read-only transition forces stopping.

Filesystem relevance:
- This file is central to online Btrfs space rebalancing and multi-device maintenance. It changes physical placement and allocation profile while preserving logical extents, checksums, tree roots, and reference accounting.

Notable risks:
- The relocation path is highly stateful and spans extent trees, checksum trees, chunk accounting, cached tree objects, open FCB extent caches, PnP volume state, and mount-manager integration.
- `start_balance()` appears to assign usage bounds from `stripes_start` / `stripes_end` when validating `BTRFS_BALANCE_OPTS_USAGE`; that is suspicious because the option fields are named `usage_start` / `usage_end`.
- `should_balance_chunk()` compares `num_stripes < opts->stripes_start || num_stripes < opts->stripes_end`; the second comparison likely intended an upper-bound check.
- Several error paths return after allocating or queueing partial relocation records; callers eventually clean queued lists, but local allocations made immediately before failed tree operations require careful audit.
- Device removal is guarded by coarse RAID-count checks, but correctness still depends on all chunks on the target device being selected and fully relocated before final removal.
