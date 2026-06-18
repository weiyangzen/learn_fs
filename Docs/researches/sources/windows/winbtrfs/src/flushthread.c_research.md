# File Research: sources/windows/winbtrfs/src/flushthread.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-7488, source bytes 262123, report `Docs/researches/chunks/chunk_sources_windows_winbtrfs_src_flushthread_c_1_1_7488_5cf62b03c528_research.md`
- chunk 2: lines 7489-7950, source bytes 13097, report `Docs/researches/chunks/chunk_sources_windows_winbtrfs_src_flushthread_c_2_7489_7950_2e9537f5de9e_research.md`

## Chunk Research

### Chunk 1: lines 1-7488

# Chunk Research: sources/windows/winbtrfs/src/flushthread.c lines 1-7488

## Scope

This chunk covers the first 7,488 lines of WinBtrfs `flushthread.c`, within subset A (`sources/windows/winbtrfs`). It is the main transactional flush implementation up to the opening of `do_write2`; the final write orchestration and flush thread entry points continue after this chunk.

## High-Level Role

The chunk implements most of the Btrfs commit machinery below the final flush loop:

- physical synchronous/asynchronous write helpers for metadata, superblocks, RAID56 partial stripes, TRIM, and disk cache flushes;
- metadata block allocation and copy-on-write update of tree extents/backrefs;
- B-tree serialization, checksum calculation, splitting, merging, and parent/root item updates;
- chunk creation, chunk deletion, block group accounting, device extent/device item updates, bootstrap system chunk array regeneration;
- file control block (`fcb`) flushing for inode items, extent data, checksums, xattrs, orphan markers, and dirty-list removal;
- directory/file reference flushing for create/delete/rename/subvolume link metadata;
- root dropping, root ref/backref maintenance, subvolume UUID metadata, orphan cleanup, and metadata-space reserve checks.

## APIs And Entry Points In This Chunk

- `write_data_phys(device, fileobj, address, data, length)`: builds an IRP_MJ_WRITE manually, supports buffered/direct/neither I/O, waits through `write_completion`, and frees MDLs/IRPs.
- `find_metadata_address_in_chunk(Vcb, c, address)`: chooses a free metadata block address inside a chunk using the chunk free-space lists and `last_alloc`.
- `get_tree_new_address(Vcb, t, Irp, rollback)`: allocates a new COW metadata address for a tree, preferring the original chunk, then other metadata/system chunks, then `alloc_chunk`.
- `do_tree_writes(Vcb, tree_writes, no_free)`: sorts/coalesces metadata write buffers, schedules `write_data`, waits for stripe completion, checks per-device write errors, and flushes pending RAID56 partial stripes.
- `calc_tree_checksum(Vcb, th)` and `calc_superblock_checksum(sb)`: support CRC32C, XXHASH, SHA256, and BLAKE2.
- `add_checksum_entry(Vcb, address, length, csum, Irp)`: rewrites checksum-tree ranges for inserted or deleted sectors, coalescing adjacent checksum items and enforcing `MAX_CSUM_SIZE`.
- `flush_fcb(fcb, cache, batchlist, Irp)`: main dirty inode flush routine for ADS xattrs, deleted inodes, extent items, inline/sparse extents, checksum updates, inode item writes, security/DOS/reparse/EA/compression/case-sensitive xattrs, and orphan markers.
- `flush_partial_stripe(Vcb, c, ps)`: reconstructs/reads missing RAID5/RAID6 stripe data, zeros unallocated/deleting ranges, then writes data and parity.
- `update_chunks(Vcb, batchlist, Irp, rollback)`: commits changed chunks, flushes RAID56 partial stripes, creates newly allocated chunks, and drops empty chunks.
- `flush_fileref(fileref, batchlist, Irp)`: emits directory index/item, inode ref, and root ref/backref changes for created, deleted, renamed, or type-changed file refs.
- `flush_disk_caches(Vcb)`: issues ATA flush-cache pass-through requests to writable devices that advertise flush support.
- `flush_subvol(Vcb, r, Irp)`: rewrites `ROOT_ITEM`s and maintains received-subvolume UUID records.
- `test_not_full(Vcb)`: calculates a Linux-style metadata reserve and returns `STATUS_DISK_FULL` when remaining metadata allocation capacity is unsafe.
- `check_for_orphans(Vcb, Irp)` and `check_for_orphans_root(Vcb, r, Irp)`: scan orphan items for dirty subvolumes, excise file extents for unlinked files, mark FCBs deleted, and remove orphan items.
- `do_write2(Vcb, Irp, rollback)`: begins at line 7481 but continues in the next chunk; this chunk only exposes its local setup.

## Core Control Flow

Metadata tree flushing follows a COW transaction sequence:

1. Mark parents of written trees with `add_parents` / `add_parents_to_cache`.
2. Normalize tree shapes with `do_splits`, including deletion of empty child trees, demotion of empty top trees, splitting oversized nodes, amalgamating underfull siblings, and removing top-level one-child parents.
3. Allocate new metadata addresses with `allocate_tree_extents` / `get_tree_new_address`; inserted extent items use skinny metadata when enabled, otherwise full `EXTENT_ITEM_TREE`.
4. Convert old tree refs with `update_tree_extents`, including shared backref handling, data/tree extent ref increments, shared ref decrements, and `reduce_tree_extent` for old blocks.
5. Update root items and free-space cache metadata via `update_root_root`.
6. Serialize dirty trees in `write_trees`, update parent item keys/addresses and extent first-item keys, calculate checksums, and send writes through `do_tree_writes`.
7. Update block group usage / changed extents with `update_chunk_usage`.
8. Update and write superblocks with backup roots through `write_superblocks`.

Chunk lifecycle control:

- `create_chunk` inserts `CHUNK_ITEM`, `BLOCK_GROUP_ITEM`, `DEV_EXTENT`s, updates `DEV_ITEM`s, optionally adds system chunks to the bootstrap array, sets `created=false`, and accounts `bytes_used`.
- `drop_chunk` trims device ranges while avoiding superblock locations, removes free-space cache files and free-space-tree entries, removes dev extents, updates device free-space/bytes-used, rewrites dev items, deletes chunk/block-group items, clears RAID incompat flags if the last such chunk is removed, removes bootstrap entries, frees chunk state, and releases/destroys locks.
- `update_chunks` decides between create/drop based on `c->created`, `c->space_changed`, and `used_minus_cache`; it deliberately subtracts self-hosted free-space-cache extents from data chunk usage before deciding a chunk is empty.

FCB/reference flush control:

- `flush_fcb` first handles alternate data streams as xattr writes/deletes, then deleted inodes, then extent changes.
- Extent flushing removes ignored extents, writes checksums for new regular extents, rationalizes unique uncompressed extents by trimming unused fronts/tails and merging adjacent physical extents, deletes old extent-data items for existing files, reinserts sparse/data/inline/prealloc extent-data items, updates inode prealloc flags, and writes inode/xattr state.
- It clears dirty-list membership under `dirty_fcbs_lock` at the end regardless of success path after `end:`.
- `flush_fileref` is the directory/link counterpart: created refs add `DIR_INDEX`, `DIR_ITEM`, and either `INODE_REF` or root ref/backref; deleted refs remove those records; rename/type changes delete old names and insert new names/indexes.

## Important State Mutated

- `Vcb->superblock`: generation-dependent roots, `bytes_used`, system chunk array (`sys_chunk_array`, `n`), backup roots, incompat flags, checksum algorithm, metadata UUID.
- `Vcb->trees`: dirty tree list, parent pointers, `write`, `has_address`, `has_new_address`, `updated_extents`, `is_unique`, `size`, `header.num_items`.
- `root`: `root_item.block_number`, `root_level`, generation fields, `bytes_used`, `treeholder`, dirty/received/orphan-check flags.
- `chunk`: free-space lists (`space`, `space_size`, `deleting`), changed extents, old/current usage, `created`, `changed`, `space_changed`, cache/old_cache, RAID56 partial stripes, device stripe references.
- `device`: `devitem.bytes_used`, trim queues, stats, device error accounting via `log_device_error`.
- `fcb`: dirty/created/deleted flags, inode item, extent list, xattr state, ADS state, orphan marker, security descriptor, DOS attributes, compression property, case-sensitivity state.
- `file_ref`: created/deleted/dirty flags, old name/index, directory cache entry metadata.
- Rollback lists are passed to space-list and extent update helpers so allocation/free-space changes can be unwound by higher-level orchestration.

## Dependencies

This code depends on Windows kernel APIs and driver conventions:

- IRP construction/completion: `IoAllocateIrp`, `IoGetNextIrpStackLocation`, `IoSetCompletionRoutine`, `IoCallDriver`, `IoFreeIrp`.
- Synchronization: `KEVENT`, `KeInitializeEvent`, `KeWaitForSingleObject`, `KeSetEvent`, `ERESOURCE`, fast mutexes, interlocked counters.
- Memory/MDL APIs: `ExAllocatePoolWithTag`, `ExFreePool`, lookaside lists, `IoAllocateMdl`, `MmProbeAndLockPages`, `MmBuildMdlForNonPagedPool`, `MmUnlockPages`.
- Storage IOCTLs and ATA pass-through: `IOCTL_STORAGE_MANAGE_DATA_SET_ATTRIBUTES`, `DeviceDsmAction_Trim`, `IOCTL_ATA_PASS_THROUGH`, `IDE_COMMAND_FLUSH_CACHE`.

It also depends on project-local Btrfs primitives:

- tree search/mutation: `find_item`, `find_next_item`, `insert_tree_item`, `delete_tree_item`, `do_load_tree`, `load_tree`, `free_tree`, `free_trees_root`;
- extent accounting: `increase_extent_refcount*`, `decrease_extent_refcount*`, `get_extent_refcount`, `get_extent_flags`, `update_extent_flags`, `find_extent_shared_*_refcount`, `update_changed_extent_ref`, `add_changed_extent_ref`;
- allocation/free-space: `alloc_chunk`, `load_cache_chunk`, `space_list_add`, `space_list_add2`, `space_list_subtract`, `space_list_merge`, `update_chunk_caches`, `load_stored_free_space_cache`;
- data I/O and RAID helpers: `write_data`, `read_data`, `sync_read_phys`, `get_raid0_offset`, `do_xor`, `galois_double`, `raid6_recover2`, `free_write_data_stripes`;
- object lifecycle helpers: `open_fcb`, `free_fcb`, `reap_fcb`, `mark_fcb_dirty`, `excise_extents`, `create_root`, `clear_batch_list`, `commit_batch_list`;
- checksum/hash implementations: CRC32C, xxHash, SHA256, BLAKE2.

## Notable Algorithms And Behaviors

- Metadata address allocation uses chunk free-space sorted by address and by size, with a `last_alloc` cursor to spread allocations inside a chunk.
- Shared metadata backref conversion is recursive and conservative. `update_tree_extents` may first update a parent to determine uniqueness, then converts shared refs to tree/data refs and adjusts `changed_extent` shadow reference lists.
- Tree splitting is simple and size-driven; comments call it naive. It maximizes filled nodes and has FIXME notes for deleted items with matching keys.
- Tree amalgamation only examines the next sibling and has a FIXME noting it does not ascend. It can merge whole sibling nodes or rebalance by moving items from the next node.
- Checksum updates rebuild the checksum range from `startaddr` to `endaddr` using a bitmap where set bits mean holes/deleted sectors and clear bits mean active checksum runs.
- Free-space cache chunks are flushed as normal FCBs during block-group usage update or dropped during chunk deletion.
- RAID56 partial-stripe flushing reads missing sectors, reconstructs degraded data if possible, zeros unallocated/deleting logical ranges, and writes parity synchronously through `write_data_phys`.
- `test_not_full` approximates future metadata allocation capacity by RAID profile, then adds currently free metadata-chunk space; it is intended to force read-only behavior before COW metadata exhaustion.

## Risks And Edge Cases

- Many operations allocate pool memory and mutate on-disk trees in steps. Errors usually return immediately, but some paths can leave in-memory dirty state partially transformed until higher-level rollback handles it.
- Several helper functions log and continue on missing optional metadata (`uuid_root`, free-space cache) but treat core tree item mismatches as `STATUS_INTERNAL_ERROR`.
- `clean_space_cache` increments `context.left` by eligible devices before issuing per-device TRIM IRPs. If IRP allocation or buffer allocation fails after the count is included, the completion event may never be signaled because `left` is not decremented on that failure path.
- `flush_disk_caches` has the same pattern: `context.left` counts all flush-capable devices, but a failed `IoAllocateIrp` jumps to `nextdev` without decrementing, risking a wait that cannot complete.
- `drop_chunk` calls `drop_chunk` while the chunk lock is already held by `update_chunks`; `drop_chunk` releases and deletes the chunk itself. Callers must not touch `c` afterward. The code has explicit comments to avoid releasing a freed lock.
- Several FIXME comments mark incomplete or approximate behavior: RAID5/6 TRIM in `clean_space_cache_chunk`, randomization in debug TRIM emulation, creation of missing checksum root, no duplicate-device optimization in `create_chunk`, naive split policy, incomplete tree amalgamation ascent, and shared flag cleanup.
- `add_checksum_entry` returns `void`; allocation or tree mutation failures are logged but not propagated to callers such as `flush_fcb`, so checksum-tree update failure may not abort the overall flush.
- `flush_fcb` clears dirty-list membership at the end even when `Status` is an error after some state mutations. Higher-level code must be careful about retry/rollback semantics.
- Root ref deletion/modification manipulates packed variable-length `ROOT_REF` arrays; truncation checks exist, but allocation and delete/reinsert ordering makes failure handling important.
- RAID56 reconstruction tolerates only limited missing stripes. Multi-device degraded cases return `STATUS_UNEXPECTED_IO_ERROR`.

## Cross-Chunk References

- `do_write2` starts at line 7481 and continues in the next chunk. This chunk establishes nearly all helper routines that `do_write2` is expected to orchestrate: orphan checks, dirty fileref/FCB/subvolume flushing, chunk updates, tree splits/allocation/writes, superblock writes, TRIM, and cache flushes.
- Final exported `do_write` and `flush_thread` are outside this chunk (function map shows them after line 7881). They likely wrap `do_write2`, rollback, scheduling, and background thread behavior.
- Batch-list execution helpers (`commit_batch_list`, `clear_batch_list`) are called here but not defined in this chunk; the final transaction ordering depends on their implementation elsewhere.
- Several declared or referenced structures and helpers (`device_extension`, `tree`, `root`, `fcb`, `chunk`, `changed_extent`, `batch_item`, `write_data_context`) are defined outside this file or earlier headers, primarily through `btrfs_drv.h`.

### Chunk 2: lines 7489-7950

# Chunk Research: sources/windows/winbtrfs/src/flushthread.c lines 7489-7950

## Scope

This chunk covers the main write-transaction finalization path for WinBtrfs, starting inside `do_write2()` after its local debug variable declarations and ending with the periodic kernel `flush_thread()` routine. It drains dirty file references, dirty FCBs, dirty subvolumes, dropped roots, chunk updates, tree allocation/splitting, free-space-cache updates, root-tree generation updates, tree writes, superblock writes, post-commit cleanup, rollback handoff, and timer-driven background flushing.

Adjacent context shows that `check_for_orphans()` immediately precedes this range and is part of the same transaction setup. The public entry point in this chunk is `do_write(device_extension* Vcb, PIRP Irp)`, declared in `btrfs_drv.h` and called from other driver paths that need to force metadata out.

## APIs And Entry Points

- `static NTSTATUS do_write2(device_extension* Vcb, PIRP Irp, LIST_ENTRY* rollback)` is the internal ordered commit pipeline. It assumes the caller holds `Vcb->tree_lock` exclusively, matching callees such as `commit_batch_list()` that annotate the same lock requirement.
- `NTSTATUS do_write(device_extension* Vcb, PIRP Irp)` initializes a rollback list, calls `do_write2()`, and either clears rollback records on success or forces the mounted volume readonly and rolls back on failure.
- `static void do_flush(device_extension* Vcb)` is the background flush wrapper. It acquires `Vcb->tree_lock`, calls `do_write()` only when `Vcb->need_write && !Vcb->readonly`, frees cached trees, logs failures, and releases the lock.
- `_Function_class_(KSTART_ROUTINE) void __stdcall flush_thread(void* context)` is the system thread entry point. It references the device object, initializes and arms `Vcb->flush_thread_timer`, waits at `Vcb->options.flush_interval`, exits on unmount/removal, skips work while `Vcb->locked`, signals `flush_thread_finished`, and terminates.

## Control Flow

`do_write2()` starts by initializing a local `batchlist` and checking orphan state for dirty file references. It then exclusively locks `dirty_filerefs_lock`, removes every `file_ref` from `Vcb->dirty_filerefs`, emits its directory/reference changes through `flush_fileref()`, releases each reference with `free_fileref()`, unlocks, and commits the accumulated batch.

Dirty FCB handling is intentionally two-pass while `dirty_fcbs_lock` is held. The first pass flushes and releases deleted FCBs before other files so deleted alternate data streams do not exhaust xattr limits and deleted normal files do not collide with reused inode metadata. After an intermediate batch commit, the second pass flushes non-root-root FCBs, acquiring each FCB `Header.Resource` around `flush_fcb()`, calling `free_fcb()`, and then committing another batch after releasing `dirty_fcbs_lock`.

Subvolume and root cleanup follows. Because the transaction holds `tree_lock` exclusively, the code drains `Vcb->dirty_subvols` without taking `dirty_subvols_lock`, calls `flush_subvol()` for each `root`, then applies `drop_roots()` if any roots are queued. `update_chunks()` writes pending chunk/device metadata into the batch and is followed by another `commit_batch_list()`.

The chunk then forces root metadata participation even for superblock-only changes. If the root tree is absent or not marked for write, it loads item zero from `Vcb->root_root` via `find_item()` and marks `root_root->treeholder.tree->write = true`, with a comment explaining Linux mount compatibility when generations must match. It also forces the extent root into cache via `add_root_item_to_cache(Vcb, BTRFS_ROOT_EXTENT, Irp)`.

If device statistics changed, `do_write2()` iterates `Vcb->devices`, flushes each `dev->stats_changed` device via `flush_changed_dev_stats()`, clears per-device flags, then clears `Vcb->stats_changed`.

The central convergence loop repeats until no free-space-cache allocation changed metadata and `trees_consistent(Vcb)` returns true. Each iteration adds parent pointers, allocates metadata tree extents, performs B-tree splits, updates chunk usage, and then either allocates legacy free-space cache items or updates the free-space-tree/chunk-cache tree when `BTRFS_COMPAT_RO_FLAGS_FREE_SPACE_CACHE` is set. A failure in legacy `allocate_cache()` is downgraded to a warning by setting `no_cache = true`; other loop failures exit through `end`.

Once trees are consistent, `do_write2()` updates the root root, writes dirty trees, checks for fullness with `test_not_full()`, optionally performs a debug-only extent-tree lookup for every tree, sets `superblock.cache_generation`, flushes disk caches unless barriers are disabled, and writes all superblocks. For volume-device children, it propagates the committed generation to every `volume_child` under `pdode->child_lock`.

Successful post-commit cleanup clears space cache state, clears each chunk's `changed` and `space_changed` flags, increments `Vcb->superblock.generation`, clears all in-memory `tree->write` flags, sets `Vcb->need_write = false`, and drains `Vcb->drop_roots`. Dropped roots with no FCBs are freed immediately; roots still referenced by FCBs are marked `dropped`.

`do_write()` wraps this with rollback semantics. Any `do_write2()` failure logs, marks the volume readonly, sends `FSRTL_VOLUME_FORCED_CLOSED` for `Vcb->root_file`, and calls `do_rollback()`; success calls `clear_rollback()`.

## State And Dependencies

Primary state is carried by `device_extension`: `need_write`, `readonly`, `locked`, `removing`, `options.flush_interval`, `superblock.generation`, `superblock.cache_generation`, `superblock.compat_ro_flags`, root pointers (`root_root`, `extent_root`), dirty queues (`dirty_filerefs`, `dirty_fcbs`, `dirty_subvols`), `drop_roots`, `devices`, `chunks`, `trees`, `vde`, and the flush-thread timer/event fields. FCB/file-ref state includes `fcb->deleted`, `fcb->subvol`, `fcb->Header.Resource`, `file_ref->fcb`, and their dirty-list links. Root state includes `root->checked_for_orphans`, `root->fcbs`, `root->dropped`, and `root->nonpaged->load_tree_lock`. Tree state includes `tree->write`, `tree->header.address`, and cached root tree holders.

The commit path depends on earlier functions in this file for transaction assembly and physical metadata work: `flush_fileref()`, `flush_fcb()`, `flush_subvol()`, `drop_roots()`, `update_chunks()`, `add_root_item_to_cache()`, `flush_changed_dev_stats()`, `add_parents()`, `allocate_tree_extents()`, `do_splits()`, `update_chunk_usage()`, `trees_consistent()`, `update_root_root()`, `write_trees()`, `test_not_full()`, `flush_disk_caches()`, `write_superblocks()`, and `clean_space_cache()`. It also depends on `treefuncs.c` helpers `commit_batch_list()`, `clear_batch_list()`, `clear_rollback()`, and `do_rollback()`, plus `free-space.c` helpers `allocate_cache()` and `update_chunk_caches_tree()`.

Windows kernel dependencies include executive resources (`ExAcquireResourceExclusiveLite`, `ExAcquireResourceSharedLite`, `ExReleaseResourceLite`, `ExDeleteResourceLite`), list primitives, pool freeing, object references, timers, events, `KeWaitForSingleObject`, `KeSetTimer`, `KeCancelTimer`, `FsRtlNotifyVolumeEvent`, and `PsTerminateSystemThread`.

## Risks And Edge Cases

- The call at line 7645 assigns `Status = commit_batch_list(...)` but does not immediately test it before root-tree forcing. A failed commit can be overwritten by later successful calls, unlike nearby commit sites that return on failure.
- `check_for_orphans()` inspects `Vcb->dirty_filerefs` just before this chunk without taking `dirty_filerefs_lock`; correctness relies on the surrounding exclusive `tree_lock` and caller discipline.
- Several early failures in `do_write2()` return directly instead of jumping to `end`; rollback is still handled by `do_write()`, but local batch cleanup is inconsistent. One `flush_fcb()` failure calls `clear_batch_list()`, while other paths after batch-producing calls may depend on callee cleanup or rollback.
- `allocate_cache()` failures are intentionally non-fatal and disable cache generation for this transaction. This preserves write progress but may leave the volume without legacy free-space-cache updates.
- `do_flush()` skips writes while `Vcb->locked`; if the timer thread repeatedly finds the volume locked, durability depends on later explicit flushes or a later timer pass.
- `flush_thread()` waits only on the timer. Shutdown/removal must cancel or satisfy the timer/wait path elsewhere, otherwise exit latency can be up to `flush_interval`.
- Dropped roots are physically freed only when their `fcbs` list is empty; otherwise they remain allocated and marked `dropped`, so later lifetime handling must respect that marker.
- The debug flush-time log for FCBs prints `filerefs` in the format string's first slot even though `fcbs` is the relevant counter, suggesting a diagnostics-only typo.

## Cross-Chunk References

- The chunk begins inside `do_write2()`; the function signature and `fcbs` debug variable start just before line 7489.
- `check_for_orphans()` at lines 7454-7479 is adjacent previous context and feeds the first status check in this range. It delegates per-subvolume orphan scanning to `check_for_orphans_root()`, which is earlier in the file.
- Most low-level metadata writers called here are defined earlier in `flushthread.c`, including tree extent allocation, split handling, chunk updates, FCB/file-ref flushing, subvolume flushing, root dropping, disk-cache flushing, and superblock writing.
- The final exported surface from this chunk is referenced across the driver: `do_write()` is used by send, PnP, scrub, balance, fsctl, create/write paths, and shutdown-style flows when `Vcb->need_write` is set. `flush_thread()` is declared in `btrfs_drv.h` and is the periodic background caller.

## Summary

This chunk is the ordered commit and background flush core for WinBtrfs. It turns dirty in-memory filesystem objects into Btrfs tree mutations, drives the metadata-allocation/split/free-space-cache convergence loop, writes trees and superblocks, advances generation state, clears dirty flags, and wraps failures by forcing the volume readonly with rollback. The final timer thread provides periodic durability while respecting mount/removal and volume-lock state.
