# File Research: sources/local-fs/btrfs-progs/check/main.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-10053, source bytes 262134, report `Docs/researches/chunks/chunk_sources_local_fs_btrfs_progs_check_main_c_1_1_10053_2da56e08050c_research.md`
- chunk 2: lines 10054-11197, source bytes 31395, report `Docs/researches/chunks/chunk_sources_local_fs_btrfs_progs_check_main_c_2_10054_11197_cfa2d051d725_research.md`

## Chunk Research

### Chunk 1: lines 1-10053

# Chunk Research: sources/local-fs/btrfs-progs/check/main.c lines 1-10053

## Scope And Position

This chunk covers almost all of `btrfs check`'s original-mode implementation in `sources/local-fs/btrfs-progs/check/main.c`, from global state and helper comparators through inode/root checks, extent/chunk/device verification, repair helpers, and the beginning of log-tree loading. The requested range ends at line 10053 inside `load_log_root()`, so log-tree orchestration and CLI command handling are cross-chunk continuations.

The file is in Research Subset A under `sources/local-fs/btrfs-progs`, a local filesystem userspace checker/repair tool. It is not kernel code, but it directly manipulates Btrfs metadata through btrfs-progs' shared kernel-format libraries.

## Public/External APIs Visible In This Chunk

- Global checker state exported/used across check modules:
  - `struct btrfs_fs_info *gfs_info`
  - accounting counters such as `bytes_used`, `total_csum_bytes`, `total_btree_bytes`, `total_fs_tree_bytes`, `total_extent_tree_bytes`, `btree_space_waste`, `data_bytes_allocated`, and `data_bytes_referenced`
  - global lists `duplicate_extents` and `delete_items`
  - mode/state flags `no_holes`, `is_free_space_tree`, `init_extent_tree`, `check_data_csum`, and `roots_info_cache`
- Non-static functions provided by this chunk:
  - `free_chunk_cache_tree(struct cache_tree *chunk_cache)`
  - `insert_block_group_record(struct block_group_tree *tree, struct block_group_record *bg_rec)`
  - `free_block_group_tree(struct block_group_tree *tree)`
  - `insert_device_extent_record(struct device_extent_tree *tree, struct device_extent_record *de_rec)`
  - `free_device_extent_tree(struct device_extent_tree *tree)`
  - `btrfs_new_chunk_record(struct extent_buffer *leaf, struct btrfs_key *key, int slot)`
  - `btrfs_new_block_group_record(struct extent_buffer *leaf, struct btrfs_key *key, int slot)`
  - `btrfs_new_device_extent_record(struct extent_buffer *leaf, struct btrfs_key *key, int slot)`
  - `check_chunks(...)`
- Main internal entry points visible in this range:
  - `do_check_fs_roots()` dispatches original vs lowmem fs-root verification.
  - `do_check_chunks_and_extents()` dispatches original vs lowmem chunk/extent verification and then runs device/super count repair checks.
  - `check_csums()` walks checksum roots.
  - `check_log_root()` validates that logged file extents have checksums in either the log root or main checksum root.

## Major Control Flow

### Startup Helpers And Mode Selection

The chunk begins with includes from btrfs-progs' kernel-compatible libraries, shared tree/disk/transaction APIs, common command utilities, and `check/*` modules. `parse_check_mode()` maps `lowmem`, `orig`, and `original` to `enum btrfs_check_mode`; `CHECK_MODE_DEFAULT` is original mode. `print_status_check_line()`, `print_status_check()`, and `print_status_return()` drive progress output using `g_task_ctx`, `is_free_space_tree`, and `check_data_csum`.

### Original-Mode Inode And Fs-Root Checking

The first large subsystem builds `inode_record` and `root_record` caches while walking fs roots:

- File extent hole helpers (`add_file_extent_hole()`, `del_file_extent_hole()`, `copy_file_extent_holes()`, `first_extent_gap()`) maintain an rbtree of logical holes for detecting discounted/overlapping file extents.
- `get_inode_rec()` creates or copy-on-writes inode records in a `cache_tree`. COW is needed because shared tree nodes can cause records to be shared across walk contexts.
- Leaf item processors collect consistency facts:
  - `process_inode_item()` records inode metadata and validates nlink/orphan, symlink flags, directory nlink, and generation/transid upper bounds.
  - `process_dir_item()` handles both `BTRFS_DIR_ITEM_KEY` and `BTRFS_DIR_INDEX_KEY`, records inode/root backrefs, validates name length and dir hash, detects duplicate directory indexes and duplicate filenames.
  - `process_inode_ref()` and `process_inode_extref()` add backrefs from inode ref items.
  - `process_file_extent()` validates inline/reg/prealloc extent layout, detects overlaps/holes, tracks found file size, validates symlink extent form, and checks csum presence for data extents.
  - `process_xattr_item()` flags overlong xattr names.
- Shared-node walk handling (`enter_shared_node()`, `leave_shared_node()`, `splice_shared_node()`) merges inode/root caches when shared B-tree blocks are encountered. This is central to original-mode deduplication of records discovered through shared subtrees.
- `walk_down_tree()` and `walk_up_tree()` perform a manual B-tree walk, including extent-ref lookup, shared-node entry/exit, readahead, parent/child checks, tree-block repair classification, and corrupt extent recording.
- `check_fs_root()` validates a single fs/subvol root: root generation, root block cleanliness, dropped-root progress, corrupt blocks, root-ref merging, inode record checks, and optional btree repair.
- `check_fs_roots()` iterates root items in the tree root, checks fs roots, processes root refs/backrefs, and invokes free-space inode checking. `do_check_fs_roots()` switches to `check_fs_roots_lowmem()` when lowmem mode is selected.

### Inode Repair Flow

The inode repair path is gated by `opt_check_repair` and is deliberately staged:

- `repair_inode_backrefs()` first deletes bad dir indexes, adds missing inode refs, adds missing dir index/item pairs, and recreates inode items when enough refs exist.
- `check_inode_recs()` performs up to three stages: delete invalid backrefs, add missing refs, then free and rescan if repairs changed metadata. It then validates the root directory and all remaining inode records.
- `try_repair_inode()` starts a transaction and applies repairs in a fixed order: bad dir hash deletion, imode reset, missing inode item rebuild, punched holes for discounted extents, directory isize reset, orphan item add, nlink repair, nbytes reset, inline ram_bytes reset, unaligned extent item deletion, and generation/transid reset.
- Repair dependencies include helpers from `check/repair.h` and `check/mode-common.h`, such as `btrfs_add_orphan_item()`, `insert_inode_item()`, `link_inode_to_lostfound()`, `delete_corrupted_dir_item()`, `detect_imode()`, and `reset_imode()`.

### Root Reference Checking

Root reference consistency is tracked separately from inode refs:

- `process_root_ref()` reads `BTRFS_ROOT_REF_KEY` and `BTRFS_ROOT_BACKREF_KEY` payloads and feeds `add_root_backref()`.
- `merge_root_recs()` converts root directory entries found while walking fs trees into root-ref records, but skips tree reloc roots.
- `check_root_refs()` marks `BTRFS_FS_TREE_OBJECTID` reachable, propagates reachability through root refs, checks expected refs from root items, verifies orphan items for unreferenced subvolumes, and reports missing dir items, dir indexes, root refs, or root backrefs.

### Extent, Backref, Chunk, And Device Checking

The second large subsystem scans all tree blocks and cross-checks extents, chunks, block groups, device extents, and device items:

- `extent_record` instances are stored in `extent_cache` and track discovered extent items, tree/data backrefs, ref counts, generation, metadata level, owner-ref validation, duplicate records, full-backref state, stripe crossing, chunk type mismatch, and corrupt-block state.
- `add_extent_rec()`, `add_tree_backref()`, and `add_data_backref()` merge facts from tree traversal, extent-tree items, and file extent items. Records are opportunistically freed by `maybe_free_extent_rec()` when all facts agree.
- `process_extent_item()` parses `BTRFS_EXTENT_ITEM_KEY` and `BTRFS_METADATA_ITEM_KEY`, validates alignment and item size, records extent refs and inline refs, checks inline-ref ordering, and updates block-group actual usage.
- `run_next_block()` is the core breadth-ish traversal loop. It chooses pending blocks with readahead preference, reads tree blocks, determines full-backref flags, checks the block, processes leaves by key type, records file extent backrefs, accounts btree/data sizes, and enqueues child nodes for later traversal.
- `parse_tree_roots()` collects normal and dropping roots. `deal_root_from_list()` processes root lists, including special drop-progress handling for partially dropped roots.
- `check_extent_refs()` is the final verifier/repairer for extent records. It pins bad extents during repair, handles duplicate extent items, validates generation, metadata level, ref counts, backpointers, owner refs, full-backref flags, stripe boundary crossing, and chunk type. Repair can delete/recreate extent records, fix full-backref flags, repair extent item generation, and restart with `-EAGAIN`.
- Chunk/device structures are created by `btrfs_new_chunk_record()`, `btrfs_new_block_group_record()`, and `btrfs_new_device_extent_record()`. `check_chunk_refs()` and `check_chunks()` reconcile chunk items against block group items and device extents, building good/bad/rebuild lists when requested. Unmatched device extents may be removed in repair mode via `btrfs_remove_dev_extent()`.
- `check_device_used()` verifies device item `bytes_used` against summed device extents and can repair it with `repair_dev_item_bytes_used()`.
- `is_super_size_valid()`, `check_super_dev_item()`, and `check_devices()` validate super/device size relationships and report device extents without a matching device.
- `check_dev_extents()` independently walks the device tree to detect overlapping dev extents and extents beyond device boundaries.
- `check_block_groups()` compares each block group's on-disk `used` with actual extent-item usage and compares summed usage with superblock `bytes_used`; repair calls `btrfs_fix_block_accounting()` and requests a rescan.
- `check_chunks_and_extents()` initializes all caches, seeds roots, scans normal and dropping roots, then runs device extent, chunk, extent-ref, block-group, and device checks. It handles repair restarts via `loop:` and cleans up all caches on exit.

### Checksum And Log Validation

- `check_extent_csums()` optionally reads all mirrored data copies and compares computed checksums against csum items.
- `check_extent_exists()` verifies that csum ranges are backed by extent items.
- `check_csum_root()` scans a checksum root for overlaps, oversized csum items, missing extent records, and optional data checksum mismatches. It skips data verification for metadump images.
- `check_csums()` iterates all checksum roots.
- `zero_log_tree()` clears log root fields in the superblock and writes supers without a full transaction.
- `check_range_csummed()` checks whether a byte range is covered by csum items in a given root.
- `check_log_root()` walks a log root, remembers the last inode requiring datasums, and verifies regular logged extents have checksums either in the log root or main checksum root.
- `load_log_root()` begins at the chunk boundary; only setup and the first assignment to `leaf = path->nodes[0]` are in scope. Adjacent context shows it reads a root item from the log tree and loads the referenced root block, but the full function belongs to the next chunk.

### Extent Tree Reinitialization And Global Repair Helpers

Repair-only helpers near the end of this chunk can rebuild major metadata:

- `btrfs_fsck_clear_root()` allocates a new empty tree block, initializes its header, inserts or updates a root item, and returns the new root block.
- `btrfs_fsck_reinit_root()` replaces an in-memory root node and updates the tree root item.
- `reset_block_groups()` reconstructs in-memory block groups from chunk items and resets allocation bit availability.
- `reset_balance()` removes balance items and tree reloc roots, then reinitializes the data reloc tree.
- `reinit_global_roots()` reinitializes all roots with a given objectid.
- `reinit_extent_tree()` refuses mixed block groups, pins or excludes existing metadata, drops/rebuilds block groups, reinitializes extent roots and optional block-group tree roots, inserts block group items, runs delayed refs, and resets pending balance.
- `delete_bad_item()` deletes bad items recorded earlier in `delete_items`, mainly malformed orphan items discovered while scanning leaves.

## State And Data Structures

Important mutable state visible in this chunk:

- `gfs_info` is the central filesystem context and is mutated for repair hooks:
  - `gfs_info->corrupt_blocks`
  - `gfs_info->fsck_extent_cache`
  - `gfs_info->excluded_extents`
  - `gfs_info->free_extent_hook`
- `inode_record` state tracks discovered inode facts, nlink/found_link, size/nbytes/isize, extent coverage, csum presence, bad hash records, unaligned extent records, and per-backref errors.
- `root_record` and `root_backref` track subvolume/root item existence, expected/found refs, reachability, and dir/root ref pairs.
- `extent_record` is the main reconciliation object for physical extents. It merges observed tree/data references with extent-tree records and records repair metadata such as duplicate extents and bad full-backref flags.
- `chunk_record`, `block_group_record`, `device_extent_record`, and `device_record` model chunk-tree, extent-tree/block-group, device-tree, and device-item views of allocation.
- `cache_tree`, rbtrees, and kernel-style lists are the dominant containers. Many records are moved between caches/lists as they become verified, repaired, orphaned, or freed.
- Global accounting counters are incremented during scanning and not locally reset in this chunk, so the top-level command path in the next chunk is responsible for initialization/summary behavior.

## Dependencies

This chunk depends heavily on:

- Btrfs shared disk/tree APIs: `btrfs_search_slot()`, `btrfs_next_leaf()`, `btrfs_read_fs_root()`, `read_tree_block()`, `btrfs_check_block_for_repair()`, `btrfs_lookup_extent_info()`, `btrfs_find_all_roots()`, `btrfs_inc_extent_ref()`, `btrfs_free_extent()`, `btrfs_update_root()`, `btrfs_update_block_group()`, delayed refs, transactions, and superblock writers.
- Shared on-disk accessors from `kernel-shared/accessors.h` and `uapi/btrfs_tree.h` for inode, dir item, file extent, root item, extent item, chunk, device item, and block group fields.
- `common/extent-cache.h`, `kernel-lib/rbtree.h`, and `kernel-lib/list.h` for cache/rbtree/list mechanics.
- Repair helpers from `check/repair.h` and `check/mode-common.h`.
- Lowmem alternatives from `check/mode-lowmem.h`, called but not implemented here.
- Quota verification headers are included but quota logic is not in this chunk.

## Risks And Edge Cases

- This code performs destructive repairs when `opt_check_repair` is set. Repair paths start transactions, delete items, recreate refs, punch holes, reset roots, prune corrupt blocks, and may restart scans with `-EAGAIN`.
- Several error paths intentionally abort or exit for cases considered unsafe or unsupported, including complex overlapping extent duplicates and failed repair aborts.
- `try_to_fix_bad_block()` appears to test `IS_ERR(root)` instead of `IS_ERR(search_root)` after `btrfs_read_fs_root()`, which is a suspicious local bug pattern in this chunk.
- `record_unaligned_extent_rec()` contains a duplicated list scan for an existing unaligned record, likely harmless but redundant.
- `process_extent_item()` reports corrupt inline refs and jumps to `out`, but returns `0`, so callers may continue after a malformed extent item unless other state records the issue.
- `free_extent_hook()` has conditions `if (!back->node.found_extent_tree && back->node.found_ref)` before freeing; after clearing found flags this looks counterintuitive and may leave or free records differently than intended.
- `check_extent_refs()` assigns `err = cur_err` each loop rather than accumulating all previous errors; final non-repair error reporting may reflect the last processed record rather than any error unless earlier records remain via other paths.
- Many processors use `BUG_ON()` for unexpected on-disk or allocation conditions. In a checker operating on corrupt filesystems, this can terminate the process instead of reporting a recoverable diagnostic.
- Full-backref inference relies on root objectid ordering and has an explicit FIXME for reclaimed root objectids.
- Repair of data backref disagreement is intentionally limited. Compressed extents and bytenr mismatches can require user-provided images/developer intervention.
- `check_extent_csums()` allocates `num_bytes` at once for each csum item range, which can be memory-heavy if malformed metadata reports a large range despite later max-entry checks.
- The chunk boundary cuts `load_log_root()` before it reads and validates log root items, so log-tree lifecycle and freeing are unresolved here.

## Cross-Chunk References

- Next chunk must complete `load_log_root()`, `check_log()`, roots-info cache handling, root item repair, global-root freshness checks, early critical root checks, command usage, and `cmd_check()`.
- This chunk calls lowmem functions implemented elsewhere: `check_fs_roots_lowmem()` and `check_chunks_and_extents_lowmem()`.
- This chunk records global lists and flags (`delete_items`, `duplicate_extents`, `found_free_ino_cache`, `found_unknown_key`, global counters) whose final reporting/cleanup is expected in the later command orchestration.
- `zero_log_tree()` is defined here but likely invoked from the later CLI/check flow.
- `reinit_extent_tree()` and `delete_bad_item()` are defined here but need the next chunk's command-level option flow to know when they are invoked.

## Summary

Lines 1-10053 implement the original-mode core of `btrfs check`: walking filesystem roots, collecting inode/root/extent/chunk/device facts, validating cross-references, and applying many repair strategies under `opt_check_repair`. The code's main pattern is to build temporary reconciliation caches from independent metadata views, free records that fully agree, report or repair records that remain, and restart scans after repairs that can invalidate caches. The chunk ends just as log-root loading begins, leaving top-level command orchestration and final log/root-item handling to the following chunk.

### Chunk 2: lines 10054-11197

# Chunk Research: sources/local-fs/btrfs-progs/check/main.c lines 10054-11197

## Scope

This report covers `sources/local-fs/btrfs-progs/check/main.c` lines 10054-11197 for subset A (`Docs/research_subset_a.md`). The chunk starts in `load_log_root()` after adjacent setup at line 10045 and then covers log-tree checking, root-item repair support, critical-root validation, the `btrfs check` usage text, the full `cmd_check()` command dispatcher, final cleanup/reporting, and `DEFINE_SIMPLE_COMMAND(check, "check")`. It does not create or update the merged per-file report.

## Public And Internal APIs Covered

- `load_log_root()` finishes loading a per-subvolume log root from a root item in the log root tree by reading the root item, constructing a `btrfs_tree_parent_check`, reading the tree block, and validating the loaded node level against the root item level.
- `check_log()` walks `gfs_info->log_root_tree` for `BTRFS_TREE_LOG_OBJECTID` root items whose offsets are filesystem root objectids, loads each temporary log root, and passes it to `check_log_root()` from the preceding chunk.
- `free_roots_info_cache()`, `build_roots_info_cache()`, `maybe_repair_root_item()`, and `repair_root_items()` implement the early root-item sanity/repair pass that detects historical stale root item bytenr/generation/level values by comparing root-tree root items against extent-tree tree-block references.
- `check_global_roots_uptodate()` verifies all global roots are readable and that each global-root generation has extent, checksum, and, when enabled, free-space-tree roots.
- `check_early_critical_roots()` validates that the tree, device, and chunk roots are uptodate before any checker stage relies on them.
- `cmd_check_usage[]` defines user-facing `btrfs check` options for superblock/root selection, operation modes, repair, checksum verification, quota report, subvolume extent reporting, progress, and deprecated space-cache clearing.
- `cmd_check()` is the command entry point: it parses CLI options, opens the filesystem, gates dangerous modes, coordinates optional one-shot operations, runs the eight main checker stages, performs deferred repair cleanups, prints summary counters, and tears down state.
- `DEFINE_SIMPLE_COMMAND(check, "check")` registers this command with the btrfs-progs command framework.

## Control Flow And Behavior

- Log checking starts by searching the log root tree for key `{ TREE_LOG_OBJECTID, ROOT_ITEM_KEY, 0 }`. It advances leaf-by-leaf until keys move past the log-root item range. For each fs-root log item it zeroes a stack `struct btrfs_root`, calls `load_log_root()`, checks the loaded root through `check_log_root()`, and frees `tmp_root.node`.
- `load_log_root()` assumes the caller's path points at the log root item. It copies the on-disk root item into `tmp_root->root_item`, sets `tmp_root->root_key`, reads the root node using owner/transid/level parent checks, and returns `-EIO` if the actual tree-block header level disagrees with the root item.
- `build_roots_info_cache()` scans the extent tree from the first extent item, increments the shared progress item counter, filters to tree-block extent or metadata items, derives the block level, and accepts only first inline refs of type `BTRFS_TREE_BLOCK_REF_KEY`. It records, per root id, the highest-level candidate root node by bytenr/generation and counts how many nodes exist at that level.
- `maybe_repair_root_item()` looks up the root id in `roots_info_cache`, rejects missing extent evidence or ambiguous top-level nodes, reads the current root item, and compares bytenr, level, and generation. In read-only checking it reports mismatch and returns `1`; in repair mode it can rewrite those fields in the leaf. It refuses to downgrade from a newer root-item generation to an older found root node.
- `repair_root_items()` first skips filesystems with `EXTENT_TREE_V2`, then builds the extent-derived root cache and scans `gfs_info->tree_root` for root items beginning at `BTRFS_FIRST_FREE_OBJECTID`. It uses a two-pass-per-leaf strategy: first scan read-only to decide whether a transaction is needed, then restart at the bad key with a transaction only for leaves that need writes. Each transaction is committed before moving to the next leaf/key range.
- Command parsing mutates global checker state: `--repair`, `--init-csum-tree`, and `--init-extent-tree` enable repair writes; `--check-data-csum` enables data checksum verification; `--mode` switches original vs lowmem checking; `--progress` initializes task reporting; `--force` bypasses mount-status blocking and drops exclusive open.
- Before opening the filesystem, `cmd_check()` checks argument count, handles the `--readonly` plus repair incompatibility, and imposes a 10-second repair warning delay unless `--force` is present. It then checks mount status, sets `OPEN_CTREE_PARTIAL` for repair, and opens `gfs_info` via `open_ctree_fs_info()`.
- After opening, repair mode refuses to proceed while device replace or balance is running. The command prints the filesystem UUID, validates critical roots, handles deprecated `--clear-space-cache`, optionally clears the tree log after user confirmation, and handles early-exit report modes (`--qgroup-report` and `--subvol-extents`).
- `--init-extent-tree` and `--init-csum-tree` run inside a transaction before normal checking. Extent-tree rebuild marks `gfs_info->rebuilding_extent_tree`; checksum-tree rebuild reinitializes checksum global roots and refills checksums, optionally after extent-tree rebuild, then commits before proceeding.
- The normal checker sequence is ordered as log, root items, extents/chunks, free-space tree/cache, fs roots, checksums, root refs, and qgroups. Progress mode wraps each stage with `task_start()` / `task_stop()` using `g_task_ctx.tp`; non-progress mode prints `[1/8]` through `[8/8]` messages.
- Some errors are fatal to later stages and branch to `out` or `close_out`, while others accumulate in `err` and continue. Fs-root and root-ref failures stop later structural checks; checksum errors are reported but intentionally non-fatal so the checker can continue.
- After root/ref/csum checks, repair mode processes `gfs_info->recow_ebs` through `recow_extent_buffer()` to fix transid errors, then drains `delete_items`, deleting bad items only in repair mode and freeing all queued records. Quota verification and possible qgroup repair run last when quotas are enabled.
- The final `out` block prints aggregate space/accounting counters, frees qgroup counts and root records, closes the ctree, deinitializes progress state, and returns the boolean-ish accumulated `err`.

## State And Data Structures

- `gfs_info` is the central filesystem handle. This chunk reads and mutates `tree_root`, `dev_root`, `chunk_root`, `fs_root`, `log_root_tree`, `global_roots_tree`, `nr_global_roots`, `super_copy`, `quota_enabled`, `recow_ebs`, and `rebuilding_extent_tree`.
- `roots_info_cache` is a process-global `struct cache_tree *` keyed by root id. Entries are `struct root_item_info` from `check/mode-original.h`, containing root level, number of highest-level nodes, root bytenr, generation, and embedded `cache_extent`.
- `root_cache` is a stack `struct cache_tree` passed across log, fs-root, and root-ref checks, then freed with `free_root_recs_tree()`.
- Command-local mode state includes selected superblock bytenr, selected tree/chunk root bytenrs, subvolume id for `--subvol-extents`, booleans for readonly, qgroup report, force, and init-csum-tree, plus `clear_space_cache` and qgroup repair counters.
- Process-wide checker flags and counters used here include `opt_check_repair`, `init_extent_tree`, `check_data_csum`, `check_mode`, `is_free_space_tree`, `no_holes`, `found_free_ino_cache`, `delete_items`, and the summary counters `bytes_used`, `total_csum_bytes`, `total_btree_bytes`, `total_fs_tree_bytes`, `total_extent_tree_bytes`, `btree_space_waste`, `data_bytes_allocated`, and `data_bytes_referenced`.
- `g_task_ctx` bridges progress reporting and item-count accounting. This chunk initializes it for progress mode and passes its `item_count` pointer to qgroup verification so qgroup scanning contributes to shared progress.

## Dependencies

- Btrfs-progs core tree APIs: `btrfs_search_slot()`, `btrfs_next_leaf()`, `find_next_key()`, `btrfs_release_path()`, `read_tree_block()`, extent-buffer read/write helpers, root/item/key accessors, feature-flag accessors, and global-root rb-tree traversal.
- Transaction and repair APIs: `btrfs_start_transaction()`, `btrfs_commit_transaction()`, `reinit_extent_tree()`, `reinit_global_roots()`, `fill_csum_tree()`, `zero_log_tree()`, `recow_extent_buffer()`, `delete_bad_item()`, `repair_qgroups()`, and repair gating via `has_running_replace_or_balance()`.
- Checker stages defined earlier or in other check modules: `check_log_root()` from the previous chunk, `do_check_chunks_and_extents()`, `validate_free_space_cache()`, `do_check_fs_roots()`, `check_csums()`, `check_root_refs()`, `qgroup_verify_all()`, `report_qgroups()`, and `print_extent_state()`.
- Common command/runtime support: `getopt_long()`, `check_argc_exact()`, `usage_unknown_option()`, `arg_strtou64()`, mount detection through `check_mounted()`, open helpers through `open_ctree_fs_info()`, UUID formatting, task utils, warning/error messaging, and the simple-command registration macro.
- Compatibility with lowmem mode is explicit: extent checking delegates to `check_chunks_and_extents_lowmem()` inside `do_check_chunks_and_extents()` outside this chunk, and root-ref checking is skipped here when lowmem fs-root checking already handled it.

## Risks And Invariants

- Root-item repair must run before other repair code. The in-code comment explains that later backref or extent-tree repair can otherwise delete or rewrite evidence needed to repair stale root items, leaving the filesystem inconsistent.
- `roots_info_cache` relies on a root having exactly one highest-level tree block. Multiple nodes at the chosen level make the root item unrecoverable here, because there is no unambiguous replacement bytenr/generation/level.
- The extent scan assumes the first inline ref of a root extent is a `TREE_BLOCK_REF`; it guards against extent items without inline refs before dereferencing. Missing this boundary check would read beyond the leaf item.
- The transaction restart loop in `repair_root_items()` is intentionally conservative to avoid committing transactions for clean leaves and rotating backup roots unnecessarily. It must release paths before commits/restarts and preserve the next key when moving across leaves.
- `cmd_check()` mixes `ret` as a detailed errno-style status with `err` as the final command failure indicator. Several branches use `err |= !!ret`; a missed update can hide a detected error, while an early `return -EIO` in the checksum-tree refill path bypasses normal cleanup.
- Repair mode on a mounted or active filesystem is dangerous. The code blocks mounted filesystems unless `--force`, removes exclusive open under force, refuses running replace/balance, and warns before repair, but `--force --repair` can still proceed with substantial corruption risk.
- Clearing the tree log in repair mode is user-confirmed because any repair transaction would otherwise invalidate log replay expectations. Failure to zero the log is treated as fatal for repair startup.
- The `--init-extent-tree` path sets `OPEN_CTREE_NO_BLOCK_GROUPS` and `gfs_info->rebuilding_extent_tree`; later extent checking depends on that state to rebuild block-group items and cannot trust metadata free space while rebuilding.
- Stage ordering is part of correctness: critical roots precede all checks; log/root-item handling precedes extent/fs-root scans; free-space validation follows extent/chunk checks; root refs follow fs roots except in lowmem mode; deferred recow/delete-item repair happens after structural scans.
- `check_global_roots_uptodate()` expects counts equal to `gfs_info->nr_global_roots` for each global root class. A typo in its error string says "chritical", but the behavior is a hard `-EIO`.

## Cross-Chunk References

- The immediately preceding chunk defines `check_range_csummed()` and `check_log_root()`, which are the actual per-log-root validators called by `check_log()` in this chunk.
- Top-of-file state outside this chunk defines `gfs_info`, summary counters, `delete_items`, checker mode flags, `roots_info_cache`, progress printing helpers, and `parse_check_mode()`; `cmd_check()` depends on all of them.
- Earlier same-file functions implement the major checker stages invoked here: root-ref validation around line 3534, fs-root checking around line 4152, checksum checking around line 6268, extent/chunk checking around line 9379, `zero_log_tree()` around line 9867, and extent-tree reinitialization around line 9709.
- Header `check/mode-original.h` defines `struct root_item_info`; `check/mode-common.h` defines `g_task_ctx` and `enum task_position`; `check/qgroup-verify.c` stores the shared qgroup item-count pointer.
- This chunk is the final chunk of `main.c`: after `cmd_check()` returns, only `DEFINE_SIMPLE_COMMAND(check, "check")` remains, so no later same-file implementation needs to be merged for command dispatch.
