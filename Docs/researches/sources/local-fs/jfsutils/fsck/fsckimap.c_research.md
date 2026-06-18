# File Research: sources/local-fs/jfsutils/fsck/fsckimap.c

## Purpose
Implements JFS fsck inode allocation map handling. It records and duplicate-checks inode extents, validates or rebuilds aggregate/fileset inode allocation maps, checks and repairs redundant primary/secondary aggregate inode structures, and contains a small append-only xtree builder used when rebuilding the secondary fileset inode map.

## Main Elements
- Workspace structures:
  - `struct fsck_iag_info` bundles the current IAG, inode-map control page, fsck imap/IAG/AG workspace tables, aggregate-vs-fileset ownership, and message context.
  - `struct xtree_buf` and static `fsim_node_pages` track rightmost xtree pages while reconstructing a fileset inode map tree.
- Free-list scanning and validation:
  - `iagfr_list_scan()` / `iagfr_list_validation()` validate the imap free-IAG list.
  - `agfrino_lists_scan()` / `agfrino_lists_validation()` validate per-AG free-inode IAG lists.
  - `agfrext_lists_scan()` / `agfrext_lists_validation()` validate per-AG free-extent IAG lists.
- Redundant aggregate inode structure checking:
  - `AIS_redundancy_check()` compares the primary and secondary aggregate inode tables and then compares the secondary aggregate inode map.
  - `AIS_inode_check()` compares special aggregate inode fields, timestamps, EA descriptor, and optional rooted tree bytes.
  - `AIM_check()` compares the primary aggregate inode map with the secondary aggregate inode map extent named by `s_aim2` and the secondary AIT root.
  - `FSIM_check()` compares primary/secondary fileset inode map leaf nodes, including non-inline leaf chains.
  - `IM_compare_leaf()` compares inode-map leaf XAD offsets, addresses, lengths, and node header fields.
- Redundant aggregate inode structure repair:
  - `AIS_replication()` rebuilds the target AIT from whichever primary/secondary table was selected as source for each part.
  - `AIS_inode_replication()` copies one source dinode to the target and adjusts `di_ixpxd` for the primary-vs-secondary table location.
  - `AIM_replication()` copies one AIM image to the other and adjusts the target root XAD and IAG `inoext[0]`.
  - `FSIM_replication()` rebuilds an independent target fileset inode-map xtree whose leaves reference the same control/IAG extents as the source.
  - `FSIM_add_extents()`, `xtAppend()`, `xtSplitPage()`, and `xtSplitRoot()` append source leaf extents into the rebuilt target xtree.
- Inode extent recording:
  - `record_imap_info()` records first-leaf offsets and root-leaf status for aggregate and fileset imaps.
  - `record_dupchk_inode_extents()` records inode extents for aggregate and fileset IAGs.
  - `record_dupchk_inoexts()` walks every allocated `inoext[]` PXD, calls `process_extent(..., FSCK_RECORD_DUPCHECK)`, and either clears corrupt inode extents in read-write mode or reports unrecoverable corruption in read-only mode.
  - `first_ref_check_inode_extents()` and `first_refchk_inoexts()` query inode extents for unresolved first references to duplicate-allocated blocks.
- IAG map rebuild/verify:
  - `iag_alloc_scan()` builds fsck truth maps (`amap`, `fextsumm`, `finosumm`) from inode records and existing IAG extent slots.
  - `iag_alloc_rebuild()` writes rebuilt pmap/wmap/summary maps, free counts, and forward list links into an IAG.
  - `iag_alloc_ver()` compares on-disk IAG maps, counts, and list membership against fsck truth.
  - `iags_rebuild()` / `iags_validation()` process all IAGs for one imap.
  - `iamap_rebuild()` / `iamap_validation()` rebuild or verify the imap control page and all IAG/list state.
  - `rebuild_agg_iamap()`, `rebuild_fs_iamaps()`, `verify_agg_iamap()`, and `verify_fs_iamaps()` are the public aggregate/fileset entry points.

## Control Flow
Early fsck phases call `record_dupchk_inode_extents()`, which first calls `record_imap_info()` so later `inode_get()`/`iag_get()` operations know where the imap leaf data begins. It then records aggregate inode-table extents and fileset inode-table extents through `record_dupchk_inoexts()`.

In read-only verification, `verify_agg_iamap()` and `verify_fs_iamaps()` fetch the imap control page and call `iamap_validation()`. That path scans free lists, builds expected IAG maps from fsck inode records, compares every IAG, validates remaining list counts, and finally checks imap control-page counters.

In read-write repair, `rebuild_agg_iamap()` and `rebuild_fs_iamaps()` call `iamap_rebuild()`. It resets control lists/counters, scans all IAGs, writes rebuilt maps and forward list links, makes a second pass to fill backward links, then writes the control page.

Redundant AIT/AIM handling is separate. `AIS_redundancy_check()` is the read-only consistency path. `AIS_replication()` is the repair path; it may use different primary/secondary sources for the filesystem inode map and the other special aggregate inodes, writes target extents with endian swapping, and updates `JFS_BAD_SAIT` when secondary replication fails.

## Dependencies And Integration
The file depends on global `sb_ptr`, `agg_recptr`, and `Vol_Label`; low-level device I/O (`readwrite_device()`, `ujfs_rw_diskblocks()`); inode/IAG access (`inode_get()`, `iag_get()`, `iag_put()`, `iag_get_first()`, `iag_get_next()`, `inotbl_get_ctl_page()`, `inotbl_put_ctl_page()`); xtree traversal (`find_first_leaf()`, `xTree_processing()`, `init_xtree_root()`); block allocation/recording (`process_extent()`, `extent_unrecord()`, `fsck_alloc_fsblks()`); workspace allocation; endian helpers; and fsck message emission.

Primary external callers are declared in `xfsckint.h` and used by `fsckmeta.c` and `xchkdsk.c`: redundancy checking in metadata verification, inode-extent recording in early block ownership passes, and imap rebuild/verification plus AIT replication in later repair/verify phases.

## Behavioral Notes
The code assumes classic JFS release-1 layout details in several places: one fileset, special aggregate inodes in the first AIT extent, and a small aggregate inode map with one IAG/root-leaf representation.

`iag_alloc_scan()` is not purely observational in read-write mode: if an inode extent is backed but none of its inodes remain allocated, it unrecords the extent, clears the IAG PXD, and reduces the backed extent count.

Secondary-repair failures are treated differently from primary-repair failures. Failure to repair the primary AIT/AIM marks the aggregate dirty; failure to repair the secondary structure warns and sets `JFS_BAD_SAIT` so future maintenance avoids trusting the flawed secondary copy.

## Risk Notes
This file is high-risk repair code because it translates fsck’s workspace truth back into allocation metadata. Incorrect IAG counts, list membership, source/target AIT selection, or extent clearing can orphan inode ranges or make allocation maps disagree with real inode usage.

Notable fragile points include endian swap boundaries around AIT writes, the positive/negative “remaining list length” validation convention, append-only xtree reconstruction for FSIM replication, and interaction between `primary_ait_4part1`/`primary_ait_4part2`.

Two apparent copy/paste hazards stand out from the implementation: `AIS_inode_check()` computes `secondary_root` from `primary_inoptr` rather than `secondary_inoptr`, so tree-byte comparison can compare the primary root with itself; and `agfrext_lists_validation()` gates free-extent validation on `frino_list_bad` rather than `frext_list_bad`.
