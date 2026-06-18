# File Research: sources/local-fs/f2fs-tools/fsck/defrag.c

## Purpose
Implements block migration for `defrag.f2fs`.

## Key functionality
- `migrate_block(sbi, from, to)`:
  - Reads one block from `from`.
  - Gets source segment type from SIT cache.
  - Writes the block to `to` with an F2FS write-life hint based on segment type.
  - Updates source and destination segment valid-block counters and valid maps.
  - Copies SSA summary from old block to new block.
  - Updates owner metadata:
    - data blocks update the owning node address via `update_data_blkaddr`.
    - node blocks update NAT via `update_nat_blkaddr`.
- `f2fs_defragment(sbi, from, len, to, left)`:
  - Flushes NAT/SIT journal entries before migration.
  - Iterates valid blocks in source range.
  - Finds free target blocks with `find_next_free_block`.
  - Migrates each valid source block.
  - Moves current segment info, zeroes journals, writes current segment info, flushes dirty SIT entries, then writes checkpoint.

## Dependencies
Uses fsck/mount/segment-layer helpers:
- `get_seg_entry`
- `get_sum_entry`
- `update_sum_entry`
- `update_data_blkaddr`
- `update_nat_blkaddr`
- `find_next_free_block`
- `move_curseg_info`
- `zero_journal_entries`
- `write_curseg_info`
- `flush_sit_entries`
- `write_checkpoint`

## Research notes
This code mutates core allocation metadata directly. Correctness depends on summary/NAT/SIT consistency updates happening as a unit before checkpoint write.
