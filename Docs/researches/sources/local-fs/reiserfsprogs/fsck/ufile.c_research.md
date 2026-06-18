# File Research: sources/local-fs/reiserfsprogs/fsck/ufile.c

`ufile.c` contains shared file-item validation, rewrite, conversion, and insertion logic used by pass 2 and semantic passes.

Key responsibilities:
- Validates file item sequences with `are_file_items_correct()`:
  - walks direct/indirect items by offset
  - detects holes, overlaps, wrong ordering, directories where file data should be, and same-type adjacent items in one node
  - computes real size and block count
  - optionally marks file items reachable
  - fixes key-format mismatches where allowed
  - detects symlink/tail cases
  - converts final indirect items back to direct items when stat data indicates they should be tails/symlinks
- Rewrites files by saving items, deleting them, optionally relocating object IDs, and reinserting items in order.
- Makes files writable before merging new items by checking/rebuilding their existing item sequence.
- Inserts first file items, creating indirect items and unformatted blocks as needed.
- Converts direct items/tails to indirect items and unformatted blocks when appending/overwriting requires block storage.
- Appends file data, including zero unformatted pointers for holes.
- Overwrites existing file regions with direct or indirect incoming data.
- Main write entry point `reiserfsck_file_write()` inserts or merges a recovered file item into the rebuilt tree.
- Maintains corruption counters for check/fix modes.

Important exported helpers:
- `delete_N_items_after_key()`
- `are_file_items_correct()`
- `rewrite_file()`
- `reiserfsck_append_file()`
- `must_there_be_a_hole()`
- `reiserfs_append_zero_unfm_ptr()`
- `reiserfsck_file_write()`
- `one_more_corruption()`
- `one_less_corruption()`

Dependencies and data flow:
- Uses relocation helpers from `pass2.c`: `objectid_for_relocation()`, `should_relocate()`, `save_and_delete_file_item()`, `insert_item_separately()`.
- Uses bitmap/allocation helpers from `ubitmap.c` and pointer checks from `pass0.c`.
- Uses semantic helpers such as `not_a_directory()` and `fix_obviously_wrong_sd_mode()`.
- Heavily depends on tree search and item mutation primitives from the ReiserFS library.

Notable behavior:
- Direct data recovered from a leaf may be copied into newly allocated unformatted nodes when the rebuilt file representation requires indirect storage.
- Incoming indirect pointers from items not already in the tree are checked with `still_bad_unfm_ptr_2()` before being marked used.
- Existing direct items may be converted to indirect items before overwrite to avoid conflicting file layouts.
- Files without stat data are skipped during pass-2 item insertion.
- If a target file remains inconsistent after rewrite, insertion is skipped rather than forcing more corruption into the rebuilt tree.
