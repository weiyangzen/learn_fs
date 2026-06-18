# File Research: sources/os/linux/linux-stable/fs/omfs/bitmap.c

## Scope

This file implements OMFS free-space accounting and allocation over the in-memory bitmap mirror loaded by `inode.c`.

## Main APIs

- `omfs_count_free()` counts free bits across `sbi->s_imap`.
- `omfs_allocate_block()` tries to allocate one exact block, updating both memory bitmap and on-disk bitmap when present.
- `omfs_allocate_range()` scans for a zero-bit run and allocates between requested minimum and maximum length.
- `omfs_clear_range()` clears allocated bits during truncation or inode eviction.

## Control Flow

- `count_run()` counts consecutive free bits across multiple bitmap buffers.
- `set_run()` updates a run in memory and in the corresponding on-disk bitmap blocks, dirtying each buffer.
- Allocation and clearing are serialized by `s_bitmap_lock`.
- Block numbers are split into bitmap page index and bit offset using `do_div()` against `8 * sb->s_blocksize`.

## Risks And Invariants

- Bitmap operations assume `s_imap` has been initialized by `omfs_get_imap()`.
- `set_run()` may span multiple bitmap blocks; failure after partial updates can leave some in-memory/on-disk bits changed.
- `omfs_allocate_block()` sets the in-memory bit before reading/updating the on-disk bitmap and does not roll it back if `sb_bread()` fails.
- The code treats missing/corrupt map indexes defensively by failing allocation or ignoring out-of-range clear requests.
