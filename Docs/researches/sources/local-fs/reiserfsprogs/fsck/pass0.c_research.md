# File Research: sources/local-fs/reiserfsprogs/fsck/pass0.c

`pass0.c` implements pass 0 of `reiserfsck --rebuild-tree`. It scans the selected block set and classifies blocks before tree reconstruction.

Key responsibilities:
- Builds auxiliary bitmaps for found leaf blocks, uniquely referenced unformatted blocks, and multiply referenced unformatted blocks.
- Selects the scan source from used blocks, whole partition, or an external bitmap, then excludes superblock, bitmap blocks, journal/reserved area, and bad blocks.
- Reads candidate blocks, identifies leaf-like blocks, and runs `pass0_correct_leaf()` to normalize leaf structure enough for later passes.
- Repairs or deletes malformed item headers: bad short keys, unknown item types, wrong key formats, item ordering problems, invalid offsets, invalid direct/indirect item shapes, and inconsistent stat-data modes.
- Verifies and repairs directory items by checking entry counts, entry locations, `.`/`..`, hash offsets, visibility bits, and `/lost+found`-style temporary names.
- Registers indirect-item unformatted pointers, zeroing pointers outside data space, into metadata/journal areas, outside the filesystem, or listed as bad blocks.
- Tracks object IDs seen in item keys and directory entries for later object-id-map rebuilding.
- Chooses the directory hash function from observed directory-entry hash hits if the superblock does not already define one.
- Saves and reloads pass-0 state as three bitmaps under `PASS_0_DONE`.

Important exported helpers:
- `is_used_leaf()`
- `is_bad_unformatted()`
- `is_good_unformatted()`
- `still_bad_unfm_ptr_1()`
- `still_bad_unfm_ptr_2()`
- `are_there_allocable_blocks()`
- `alloc_block()`
- `make_allocable()`
- `is_bad_item()`
- `is_leaf_bad()`
- `load_pass_0_result()`
- `pass_0()`

Dependencies and data flow:
- Uses global `fs`, `fsck_data(fs)`, pass statistics, ReiserFS bitmap helpers, item/key helpers, `bread()`/buffer-cache APIs, and balancing/file helpers declared through `fsck.h`.
- Produces the leaf/unformatted classification consumed by pass 1 and allocation routines.
- Produces an object-id map later flushed into the superblock/object-id area.

Notable behavior:
- Pass 0 is heuristic and repair-oriented. It may delete items from leaf blocks during normalization if it cannot infer a safe correction.
- In `FSCK_CHECK`/`FSCK_AUTO`, some structural problems are counted as fixable/fatal rather than repaired.
- Hash mismatch can cause a whole leaf to be skipped as “too old” for the selected hash.
- Many invariants use `die()`/`reiserfs_panic()` because later rebuild passes assume pass 0 removed impossible metadata.
