# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsresize.c

## File Role

`ntfsresize.c` implements the `ntfsresize` command-line utility for resizing NTFS volumes without intentional data loss. It supports:

- consistency checks only (`--check`)
- size estimation (`--info`, `--info-mb-only`)
- shrinking to an explicit size (`--size`)
- growing to the current device size by default
- an experimental expansion mode that moves an existing NTFS filesystem toward the beginning of an enlarged partition (`--expand`)
- read-only dry runs (`--no-action`)
- bad-sector guarded operation (`--bad-sectors`)

The file is a standalone procedural utility built on libntfs-3g APIs. It directly manipulates NTFS metadata including `$Bitmap`, `$BadClus`, `$MFT`, `$MFTMirr`, `$Boot`, volume flags, and mapping pairs.

A key maintenance warning appears near the top: external tools grep for several user-facing messages, so many output strings are intentionally stable and marked with warnings not to modify them.

## Major Dependencies

The file includes ntfs-3g internal headers for all filesystem manipulation:

- `device.h`, `volume.h`, `bootsect.h` for device and boot sector access
- `attrib.h`, `inode.h`, `mft.h`, `runlist.h`, `bitmap.h` for NTFS metadata and mapping-pair work
- `utils.h`, `misc.h`, `support.h`, `debug.h`, `endians.h`, `types.h`, `param.h`

It depends on libntfs-3g primitives such as:

- `ntfs_mount`, `ntfs_umount`, `ntfs_check_if_mounted`
- `ntfs_inode_open`, `ntfs_inode_close`, `ntfs_file_record_read`
- `ntfs_attr_open`, `ntfs_attr_lookup`, `ntfs_attr_truncate`, `ntfs_attr_update_mapping_pairs`
- `ntfs_mapping_pairs_decompress`, `ntfs_mapping_pairs_build`, `ntfs_get_size_for_mapping_pairs`
- `ntfs_mst_pread`, `ntfs_mst_pwrite`, `ntfs_pread`, `ntfs_pwrite`
- `ntfs_volume_get_free_space`, `ntfs_volume_write_flags`, `ntfs_logfile_reset`
- NTFS bitmap helpers such as `ntfs_bit_get`, `ntfs_bit_set`, `ntfs_bit_get_and_set`, `ntfs_bitmap_set_run`

## Core Data Structures

`opt` is a file-global command option state. It tracks verbosity, dry-run/read-only mode, force count, info modes, expand mode, progress-bar display, bad-sector override, explicit target bytes, and target volume path.

`struct bitmap` holds an in-memory allocation bitmap with byte size and raw bytes.

`struct progress_bar` tracks progress start/stop, resolution, display flags, and percent scaling.

`struct llcn_t` stores the last logical cluster number seen for a metadata category and the inode that caused it. These values drive shrink-size advice.

`struct DELAYED` queues runlist updates that cannot be written in place because their mapping pairs no longer fit in the current MFT record. Delayed records preserve attribute type, inode reference, VCN base, optional attribute name, replacement runlist, and original runlist allocation ownership.

`ntfsck_t` is the consistency-check context. It stores the current inode and attribute context, counted in-use clusters, duplicate references, out-of-volume references, reporting controls, flags, and the reconstructed LCN bitmap.

`ntfs_resize_t` is the main shrink/grow context. It stores the mounted volume, current inode/record/attribute, target size in clusters, relocation counters, `$MFTMirr` placement, dirty state, shrink flag, bad cluster count, MFT relocation state, delayed runlists, progress state, allocation bitmap, last-used-cluster statistics by feature class, unsupported-cluster boundary, and mirror-copy source.

`expand_t` is separate state for `--expand`. It intentionally duplicates some resize logic while operating before a normal mount is possible. It tracks old/new sector counts, metadata sizes and placement, byte/sector/cluster offset between old and new layout, copied boot sector, MFT bitmap, allocation bitmap, scratch MFT record, progress, and delayed runlists.

## CLI and Option Handling

`parse_options()` supports short and long options:

- `-c`, `--check`
- `-i`, `--info`
- `-m`, `--info-mb-only`
- `-s SIZE`, `--size SIZE`
- `-x`, `--expand`
- `-n`, `--no-action`
- `-b`, `--bad-sectors`
- `-f`, `--force`
- `-P`, `--no-progress-bar`
- `-v`, `--verbose`
- `-V`, `--version`
- `-h`, `--help`
- `-d`, `--debug` when built with `DEBUG`

Important behavior:

- exactly one device argument is required except for help/version
- `--info` and `--info-mb-only` force read-only mount mode
- `--size` is mutually exclusive with `--info`, `--info-mb-only`, and `--expand`
- `--expand` is mutually exclusive with `--info-mb-only`
- stderr is redirected to stdout so progress and error messages remain in one stream
- debug stderr is suppressed unless `--debug` is set in debug builds

`get_new_volume_size()` parses decimal byte sizes and optional `k`, `M`, `G` suffixes. A two-character suffix ending in `i` switches from SI base 1000 to binary base 1024. Unsuffixed sizes are marked as reliable for backup boot sector placement because they imply exact bytes.

## Error Handling and User Interaction

The file centralizes formatted output in:

- `perr_printf()`
- `err_printf()`
- `err_exit()`
- `perr_exit()`

Errors are intentionally emitted to stdout with stable `ERROR` prefixes. `proceed_question()` asks for interactive confirmation before dangerous operations unless forced.

Several long static warning strings are reused for common risk conditions:

- invalid NTFS selection
- inconsistent/corrupt volume
- hibernated Windows state
- unclean journal
- already-opened volume
- bad-sector risk
- severe bad-sector risk
- final partition-resizing instructions after shrink

## Consistency Check Path

The consistency check rebuilds an allocation view from MFT records and compares it against `$Bitmap`.

`setup_lcn_bitmap()` allocates an initially clear bitmap and marks clusters beyond the volume as used.

`build_allocation_bitmap()` iterates every MFT record based on `$MFT` initialized size. It skips unreadable `EIO`/`ENOENT` records and base records for extents, then calls `walk_attributes()`.

`walk_attributes()` iterates attributes in an inode. For each non-resident attribute, `build_lcn_usage_bitmap()` decompresses mapping pairs, skips holes/unmapped runs, validates LCN and length, detects references outside the volume, detects duplicate cluster references, and marks every referenced cluster in the reconstructed bitmap.

`compare_bitmaps()` reads the real `$Bitmap` data and compares byte-by-byte and bit-by-bit against the reconstructed bitmap. It allows one special backup boot sector case at the volume midpoint, but otherwise any mismatch reports cluster accounting failure and aborts as corruption.

`check_cluster_allocation()` ties these pieces together and fails if there are duplicate references, out-of-volume references, or bitmap mismatches.

## Bad Sector Handling

`lookup_data_attr()` locates named or unnamed `$DATA` attributes for a metadata inode.

`open_badclust_bad_attr()` opens `$BadClus:$Bad` and maps its runlist.

`check_bad_sectors()` counts real allocated runs in `$BadClus:$Bad`. If any bad clusters are present, resizing aborts unless `--bad-sectors` is provided. With the override, it continues but prints strong reliability warnings.

`truncate_badclust_bad_attr()` truncates `$BadClus:$Bad` to match the new volume cluster count and clears sparse indicators in the inode/attribute metadata.

`truncate_badclust_file()` drives the update for `$BadClus`.

## Resize Constraint Collection

`set_resize_constraints()` iterates all active base MFT records and calls `resize_constraints_by_attributes()`.

`build_resize_constraints()` decompresses each non-resident runlist and calls:

- `collect_resize_constraints()` to record last-used clusters by supported/unsupported feature class
- `collect_relocation_info()` when shrinking to count clusters beyond the target size that must be relocated

Feature classifications include:

- `$Bitmap`
- files with attribute lists / multi-record attributes
- sparse attributes
- compressed attributes
- `$MFTMirr`
- ordinary attributes

Unsupported cases influence `last_unsupp`, which determines the smallest supported shrink target. Fragmented `$Bitmap` with an attribute list and fragmented `$MFTMirr` data are explicitly unsupported.

`set_disk_usage_constraint()` also ensures the reported minimum cannot go below the amount of used space.

`check_resize_constraints()` enforces shrink feasibility:

- full volumes cannot shrink
- target size must not be below used clusters
- target size must be above the unsupported-fragmentation boundary
- info modes report advice instead of aborting on normal target-size constraints

`advise_on_resize()` and `print_advise()` print the minimum supported shrink size and, in verbose mode, the limiting metadata categories and inodes.

## Runlist and Cluster Allocation Helpers

The utility performs in-memory runlist surgery before writing updated mapping pairs.

Important helpers:

- `rl_set()` initializes a runlist element.
- `rl_items()` counts elements including terminator.
- `rl_fixup()` removes leading/trailing unmapped placeholder runs and rejects unmapped runs in the middle.
- `replace_runlist()` merges a replacement partial runlist into a full existing runlist.
- `replace_attribute_runlist()` rebuilds mapping pairs and either writes them into the current MFT record or queues a delayed update if the attribute header must grow beyond the record.
- `replace_later()` records a delayed runlist replacement, prioritizing `$MFT` updates before non-MFT updates.
- `delayed_updates()` reloads MFT state, applies queued updates, records MFT extents in the MFT bitmap when necessary, and handles special ordering for no-action mode.

Cluster allocation for relocation uses the reconstructed/resized bitmap:

- `find_free_cluster()` searches for a sufficiently large free range under the new volume boundary, with a static scan position and optional midpoint hint.
- `alloc_cluster()` builds one or more runlist entries until the requested number of clusters is allocated.
- `set_bitmap_range()`, `set_bitmap_clusters()`, and `release_bitmap_clusters()` maintain the in-memory allocation bitmap.
- `max_free_cluster_range` is a file-global optimization/constraint for repeated allocation attempts.

## Shrink Relocation Flow

`relocate_inodes()` handles data movement before metadata truncation.

Key sequencing:

1. It initializes progress with the previously counted relocation total.
2. It allocates a scratch MFT record.
3. If the first `$MFT:$DATA` run crosses the target boundary, it preallocates a new first MFT chunk that must contain at least 16 MFT records.
4. It walks all inodes once to relocate non-MFT-data attributes.
5. It then walks MFT data attributes from high VCN downward so the old MFT remains readable while being moved.

Per-inode work:

- `relocate_inode()` reads an MFT record, skips unused records, sets current MFT reference and dirty state, then calls `relocate_attributes()`.
- `relocate_attributes()` walks attributes, skips unsupported/irrelevant cases such as `$Bitmap:$DATA` and `$BadClus:$DATA`, and calls `relocate_attribute()`.
- `relocate_attribute()` decompresses mapping pairs, validates runs, and calls `relocate_run()` on each real run.

Per-run work:

- `relocate_run()` ignores runs fully below the target boundary.
- If a run crosses the boundary, it splits the run at the new end using `rl_split_run()`.
- If a run lies beyond the target boundary, it allocates replacement clusters below the target, copies data with `relocate_clusters()`, and replaces the old runlist segment with `rl_insert_at_run()`.
- `$MFTMirr` and the first `$MFT` run receive special placement and mirror-source tracking.

Cluster copying is performed by `copy_clusters()`, which reads and writes whole clusters through the NTFS device ops and updates progress. Bad I/O errors print bad-sector warnings.

## Metadata Truncation and Final Shrink Updates

After relocation, the normal resize path updates metadata in this order:

1. `prepare_volume_fixup()` marks the volume dirty and resets `$LogFile`, scheduling Windows `chkdsk`.
2. `relocate_inodes()` moves data if relocation was needed.
3. `truncate_badclust_file()` updates `$BadClus:$Bad`.
4. `truncate_bitmap_file()` rebuilds and writes `$Bitmap`.
5. `delayed_updates()` applies any queued attribute-list / runlist expansions.
6. `update_bootsector()` writes the new sector count and updates `$MFT` / `$MFTMirr` boot-sector LCNs if needed.
7. The device is synced, success is reported, and shrink-specific partition recreation advice is printed.

`truncate_bitmap_data_attr()` computes the new bitmap byte size, reallocates `$Bitmap` clusters, resizes cached volume bitmap metadata, writes the updated bitmap data, and switches the cached `$Bitmap` runlist when replacement was immediate.

`update_bootsector()` reads the boot sector, updates `number_of_sectors`, handles `$MFTMirr` copying from the correct source, updates `mft_lcn` if `$MFT` moved, writes the primary boot sector, and conditionally writes a backup boot sector when the requested byte size is exact and sector-aligned.

## Mount and Safety Checks

`mount_volume()` first checks mount state. It refuses write operations on mounted devices and refuses read-only mounted devices unless the requested operation is read-only. It then mounts with `NTFS_MNT_FORENSIC` to avoid mount-time modifications.

It rejects:

- dirty volumes unless `--force` is supplied
- cluster sizes above `NTFS_MAX_CLUSTER_SIZE`
- unsupported NTFS versions
- devices smaller than the current NTFS volume

`check_volume()` maps mount failures to user-facing explanations for invalid NTFS, corruption, hibernation, unclean journal, or busy/opened volume.

## Experimental `--expand` Mode

The large second half of the file implements expansion toward the beginning of a partition. The comments emphasize that this code is newer, partially separate from the older resize path, and should eventually be deduplicated after it is considered safe.

This mode does not mount the volume initially. It reads the old volume parameters from the backup boot sector at the end of the current partition because the beginning of the partition may contain unrelated old data after partition merging.

High-level flow:

1. `expand_to_beginning()` opens the raw device and determines sector size/device size.
2. `get_volume_data()` reads and validates the backup boot sector, parses old NTFS parameters, allocates scratch state, and calls `can_expand()`.
3. `can_expand()` computes cluster/sector/byte increment, validates backup boot sector match, computes required metadata sizes, verifies that `$Boot`, `$Bitmap`, and `$MFT` fit in the expanded space, checks cluster alignment, optionally prints minimum expansion advice, and validates metadata constraints.
4. `really_expand()` allocates the new bitmap and old MFT bitmap, warns the user, rebases all MFT records into the new location, writes the new bitmap, copies `$MFT` to `$MFTMirr`, copies `$Boot`, remounts the updated volume, applies delayed runlist updates, fixes index sizes, writes the backup boot sector, syncs, and unmounts.

Important expansion helpers:

- `find_attr()`, `get_unnamed_attr()`, `read_and_get_attr()` locate attributes directly inside raw MFT records.
- `get_data_size()` reads allocated size of unnamed `$DATA`.
- `get_mft_bitmap()` reads the old MFT bitmap using rebased cluster positions.
- `check_expand_constraints()` rejects unsupported cases: fragmented `$MFT` with attribute list, fragmented `$MFTMirr`, fragmented `$Boot`, dirty volume unless forced, and problematic `$BadClus`.
- `set_bitmap()` marks runs in the new allocation bitmap and detects accidental reallocation.
- `rebase_runlists()` offsets all non-resident runlists in a normal MFT record by `cluster_increment`.
- `rebase_runlists_meta()` handles metadata files whose unnamed data is moved into the newly created metadata area: `$Boot`, `$Bitmap`, `$MFT`, and `$BadClus`.
- `rebase_inode()` reads an old MFT entry, rebases or creates a minimal unused record, and writes it into the new MFT.
- `rebase_all_inodes()` starts from old `$MFT`, computes the inode count, and rebases every MFT record into the new location.
- `copy_boot()` writes the new `$Boot` data and adjusts hidden sectors for Windows bootability.
- `copy_mftmirr()` copies selected new MFT records to the old `$MFTMirr` location plus offset.
- `write_bootsector()` writes the final backup boot sector; comments note that after this point the resize cannot simply be rerun.

No-action mode in expansion can rebase and validate much of the operation, but it explicitly cannot complete the final remount/check path.

## Main Function Flow

`main()` performs:

1. set NTFS log handler
2. print program/version
3. parse options
4. initialize locale
5. `--check`: mount/check volume only and exit
6. `--expand`: run expansion path without normal initial mount
7. normal mount and device-size validation
8. derive target size:
   - explicit `--size`
   - current device size by default when not info mode
   - reserve one sector for backup boot sector
9. reject no-op resize
10. initialize `ntfs_resize_t`
11. check bad sectors
12. reconstruct and compare allocation bitmap
13. print disk usage
14. collect resize constraints and relocation needs
15. report info/advice if requested
16. confirm dangerous writes unless forced or dry-run
17. mark volume dirty and reset logfile
18. relocate clusters if needed
19. update `$BadClus`, `$Bitmap`, delayed runlists, and boot sector
20. in dry-run, report success and exit
21. sync device, print success, print shrink partition advice, free bitmap, unmount

## Important Invariants and Ordering Constraints

- User-facing messages marked as grep-sensitive should be treated as compatibility surface.
- The reconstructed allocation bitmap must match `$Bitmap` before resizing proceeds.
- Bad sectors abort unless explicitly overridden.
- The old MFT must remain readable while processing non-MFT records, so `$MFT:$DATA` relocation is split into special phases.
- `$MFT` delayed updates must be processed before ordinary delayed updates so new extents are stored in the correct MFT location.
- In no-action mode, `$MFT:$DATA` delayed update ordering is altered so reads still use the old MFT.
- `$Bitmap` cannot be treated like ordinary data during relocation; it is rebuilt/truncated separately.
- `$BadClus:$Bad` is not relocated as normal data and is truncated/expanded through special handling.
- `$MFTMirr` is constrained to simple layouts in multiple places.
- Boot-sector update happens late, after metadata changes, because it commits the new volume geometry.
- Expansion mode delays final backup boot sector rewrite until the end because it removes the ability to safely rerun the expansion.

## Error and Risk Profile

This file is high-risk filesystem surgery code. Notable risks and maintenance concerns:

- It uses file-global state (`opt`, `max_free_cluster_range`, and static allocation search position) that makes behavior non-reentrant.
- Many operations abort the process directly with `exit()` or `err_exit()`, which is acceptable for a command-line utility but makes reuse difficult.
- There is manual memory ownership across runlist replacement and delayed queues; delayed runlists intentionally transfer ownership.
- Several comments identify unsupported or incomplete cases, including highly fragmented `$Bitmap`, fragmented `$MFTMirr`, resident `$Bitmap`, fragmented expansion metadata, MFT extents in expansion mode, and future deduplication needs.
- Expansion mode directly edits raw records before a normal mount and is explicitly labeled experimental.
- Some size parsing and multiplication paths have comments noting missing overflow checks.
- The code intentionally does not always close volumes on all paths due to `CLEAN_EXIT 0`, matching historical behavior.
- `read_all()` and `write_all()` treat read-only mode as successful without touching the device, which is central to dry-run behavior but unusual if read in isolation.

## Testing and Verification Relevance

Useful tests for this file would need image-backed NTFS volumes rather than ordinary unit tests. High-value scenarios include:

- option parsing conflicts and size suffix parsing
- read-only `--info` and `--no-action` paths
- clean shrink with no relocations
- shrink requiring ordinary file relocation
- shrink requiring `$MFT` relocation
- `$MFTMirr` relocation
- `$Bitmap` growth/shrink
- bad-sector list present with and without `--bad-sectors`
- mounted read-only and mounted read-write rejection
- dirty volume with and without `--force`
- unsupported fragmented metadata cases
- expansion dry-run and real expansion on disposable images
- exact backup boot sector write behavior for unsuffixed sector-aligned sizes

## Summary

`ntfsresize.c` is the core NTFS resizing implementation in ntfs-3g. It combines a lightweight fsck-style cluster accounting pass, shrink feasibility analysis, cluster relocation, metadata truncation/reallocation, boot-sector updates, and a separate experimental expansion algorithm. The code is careful about on-disk update ordering and user-visible safety warnings, but it is also procedural, stateful, and full of special cases required by NTFS metadata layout.
