# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/cow_repair.c

## Role

Repairs an inode’s in-core CoW fork mappings by replacing bad unwritten CoW staging extents with freshly allocated CoW staging space and reaping the old blocks.

## Key Functions

- `xrep_bmap_cow()` is the top-level repair entry point for CoW fork mappings.
- `xrep_cow_find_bad()` and `xrep_cow_find_bad_rt()` scan refcount and rmap metadata for normal and realtime CoW staging extents.
- `xrep_cow_mark_shared_staging()`, `xrep_cow_mark_missing_staging()`, and `xrep_cow_mark_missing_staging_rmap()` mark file-offset ranges requiring replacement.
- `xrep_cow_alloc()` and `xrep_cow_alloc_rt()` allocate replacement CoW staging extents and create refcount CoW records.
- `xrep_cow_find_mapping()` revalidates current CoW fork extents under the inode lock.
- `xrep_cow_replace_mapping()` and `xrep_cow_replace_range()` splice replacement mappings into the CoW fork.
- `xrep_cow_replace()` walks bad file-offset ranges and replaces them in manageable chunks.

## Repair Constraints

- Requires rmapbt and reflink.
- Ignores delalloc CoW records because they are incore only.
- Ignores written CoW extents because writeback may already be in flight.
- Rejects realtime files with large realtime allocation units and metadata inodes on realtime storage.
- Reaps discarded blocks as CoW-owned metadata, not inode-owned data.

## Research Notes

On-disk metadata does not record ownership of CoW fork mappings directly, so repair can only infer badness from refcount/rmap discrepancies. The strategy is conservative: replace only unwritten mappings that are shared, missing CoW staging records, cross-linked, or forcibly rebuilt.
