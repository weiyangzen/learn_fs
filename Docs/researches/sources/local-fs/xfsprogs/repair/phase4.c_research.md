# File Research: sources/local-fs/xfsprogs/repair/phase4.c

## Role

`phase4.c` implements phase 4: detect duplicate block claims, reprocess inodes against duplicate extent lists, collect rmap/refcount data, validate quota inode pointers, and check realtime metadata before rebuild.

## Duplicate Extent Setup

`process_dup_extents` walks the in-core block map for one AG or rtgroup and:

- Warns about free space seen by only one freespace btree in no-modify mode.
- Adds `XR_E_MULT` data-device ranges to the per-AG duplicate extent tree.
- Ignores duplicate rtgroup extents because no later search consumes them.
- Warns on unknown/bad block states.

`process_dup_rt_extents` scans the legacy realtime extent bitmap and builds merged duplicate realtime extent ranges.

## Inode Reprocessing

Phase 4 resets all bmaps, then calls inode processing with:

`process_aginodes(..., check_dirs=0, check_dups=1, extra_attr_check=0)`

This gives each inode a two-pass duplicate check:

- First pass checks whether the inode overlaps known duplicate extents.
- If corrupt, the inode/fork can be cleared.
- If clean, the second pass updates block ownership maps.

Directory and attr semantic checks are disabled because phase 3 already handled them.

## Root and Metadata Root Checks

Before duplicate processing, phase 4 checks whether the root inode and metadir root inode are free or not directories. If so, it sets global reconstruction flags and reports loss.

## Rmap and Refcount Processing

When rmap work is needed, `collect_rmaps` is enabled before inode reprocessing. `process_rmap_data` then:

- Adds fixed AG/rtgroup rmap records.
- Verifies rmap btrees.
- Computes data and realtime refcount records when reflink is enabled.
- Fixes inode reflink flags.
- Checks refcount btrees.

## Quota Superblock Validation

`quotino_check` verifies that remembered quota inode numbers are valid, present in the inode tree, and not free. Missing quota inodes are marked lost.

`quota_sb_check` reconciles quota feature state:

- For metadir filesystems, discovered quota inodes can preserve or enable quota feature state.
- For older layouts, losing all quota inodes downgrades quota state; valid quota inode triplets enable it.

## Realtime Metadata

If realtime blocks exist, phase 4 calls `check_rtmetadata` after duplicate processing to generate/check realtime summary and bitmap information before later rebuild phases.

## Memory Lifecycle

After inode duplicate processing, phase 4 frees realtime duplicate extent tracking and per-AG duplicate extent trees as AG work completes.

## Interactions

Phase 4 is the bridge between inode scans and allocation metadata rebuild. It converts block ownership conflicts into duplicate extent lists, lets inode repair remove bad claimants, and then produces a clean block state map for later freespace reconstruction.
