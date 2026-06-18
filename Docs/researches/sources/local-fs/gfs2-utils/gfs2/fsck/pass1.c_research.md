# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/pass1.c

## Purpose
Implements fsck pass 1: scans dinodes from resource-group bitmaps, validates inode format/type, metadata trees, data pointers, directory leaves, extended attributes, block counts, system inodes, duplicate references, and builds the primary block/link maps used by later passes.

## Main Elements
- Block map state:
  - Static `bl`: two-bit fsck blockmap for discovered block state.
  - `blockmap_set()`, `_fsck_blockmap_set()`, `fsck_blockmap_set()`: synchronize fsck blockmap with rgrp bitmap repairs.
  - `blockmap_create()`, `link1_create()`, `bmap_create()`, destroy helpers, and `enomem()`.
- Pass1 metawalk callbacks:
  - `p1_check_metalist()`: validates indirect/hash-table blocks, detects duplicates, zeroes bad indirect pointers if approved.
  - `p1_check_data()`: validates data pointers, classifies duplicate data/meta/dinode conflicts, and adds duplicate refs.
  - `p1_check_leaf()`: marks exhash directory leaf blocks and records duplicate leaf references.
  - `p1_repair_leaf()`: patches bad directory leaf references by zeroing hash table slots.
  - EA callbacks validate indirect EA blocks, EA leaves, EA entries, and extended EA data blocks.
  - Undo callbacks reverse metadata/data work when an inode is invalidated.
- Range checking:
  - `rangecheck_block()` and related callbacks preflight inodes for excessive invalid/duplicate pointers before destructive cleanup.
- Inode processing:
  - `set_ip_blockmap()` classifies dinodes by mode and inserts directories into the directory tree.
  - `handle_ip()` orchestrates rangecheck, dinode marking, link tracking, metadata/data/EA checks, lost+found reprocessing, and block-count repair.
  - `handle_di()` loads an inode from a dinode buffer, repairs bad inode address fields, checks allocation goal, and calls `handle_ip()`.
- System inode repair:
  - `resuscitate_metalist()` / `resuscitate_dentry()` keep system directory contents alive.
  - `check_system_inode()` validates or rebuilds master, root, inum, statfs, jindex, rindex, quota, per_node, and journals.
  - Builders wrap libgfs2 creation for root, master, per_node, inum, statfs, rindex, quota, and journals.
- Resource-group scan:
  - `pass1_process_rgrp()` scans each rgrp bitmap for dinodes.
  - `pass1_process_bitmap()` reads each dinode candidate, detects invalid/duplicate dinodes, and dispatches inode handling.
- `pass1()`: allocates maps, checks system inodes, marks rgrp metadata blocks, processes every rgrp, then calls `pass5(cx, bl)` to reconcile bitmaps.

## Control Flow
Pass 1 first creates `bl`, `nlink1map`, and `clink1map`. It validates system inodes before scanning user dinodes. For each resource group it marks rgrp header/bitmap blocks as used, scans bitmap dinode states, skips already-processed system inodes, validates dinode headers, processes inode metadata and EA trees via metawalk, records duplicates, and tracks link counts. After scanning, it invokes pass5 immediately to reconcile discovered block state with on-disk bitmaps.

## Dependencies And Integration
Uses `metawalk.c` as the traversal engine; duplicate tracking and delete helpers from fsck common code; journal/per_node builders from libgfs2 and recovery code; link accounting from `link.c`; inode tree helpers; and global progress/abort state from `main.c`.

## Risk Notes
Pass1 is intentionally destructive under query control: it can mark dinodes free, zero indirect pointers, remove extended attributes, repair block counts, rebuild system inodes, allocate system structures, and rewrite bitmap/rgrp accounting. Its preflight bad-pointer tolerance is a safety guard against treating garbage pointer fields as authoritative.
