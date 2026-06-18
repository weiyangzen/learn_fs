# File Research: sources/os/linux/linux/fs/ntfs3/index.c

## Role

Implements NTFS index B-tree operations used for directories and metadata indexes such as `$Secure::$SII`, `$Secure::$SDH`, `$ObjId:$O`, `$Quota:$Q`, and `$Reparse:$R`. It provides key collation, index bitmap scanning, index-buffer I/O and validation, sorted/raw traversal, insertion with splitting, deletion with subtree cleanup, and duplicate-info updates.

## Key Structures and Constants

- `s_index_names[]` maps internal index mutex classes to index attribute names: `$I30`, `$SII`, `$SDH`, `$O`, `$Q`, `$R`.
- `struct bmp_buf` wraps resident or nonresident index bitmap access, including buffer-head state and valid-size extension tracking.
- `struct ntfs_fnd` is used as a search path/cache across root and allocation-buffer levels; this file clears, pushes, pops, and reuses finder state.

## Collation

- `cmp_fnames()` compares NTFS filename keys using the volume upcase table and mount case-sensitivity policy; it handles CPU-side search names and on-disk `ATTR_FILE_NAME` keys.
- `cmp_uint()` handles integer indexes such as `$SII` and quota `$Q`.
- `cmp_sdh()` orders `$SDH` by security hash and, when requested, security id.
- `cmp_uints()` compares multi-u32 keys for `$O` and `$R`; it has a reparse-removal mode that ignores the reparse tag and compares by file reference.
- `get_cmp_func()` selects the comparison function from an `INDEX_ROOT` type and collation rule.

## Bitmap and Buffer Handling

- `bmp_buf_get()` and `bmp_buf_put()` map resident/nonresident index bitmap storage, zero invalid tails, update valid size, and mark metadata dirty.
- `indx_mark_used()` and `indx_mark_free()` update individual index allocation bits.
- `scan_nres_bitmap()` scans nonresident bitmap blocks under `indx->run_lock`, loading run ranges lazily when needed.
- `indx_find_free()` finds a free index allocation bit; `indx_used_bit()` finds the next used bit for enumeration.

## Validation and Read/Write

- `index_hdr_check()` validates index header offsets, used size, total size, and minimum directory-entry presence.
- `index_buf_check()` validates `INDX` signature, update-sequence array placement/count, VBN, and embedded header.
- `indx_init()` validates an `INDEX_ROOT`, records index block sizing, VBN/VBO shift values, type, and initializes the run lock.
- `indx_read_ra()` reads an index allocation buffer via runlist and fixups, loads missing run ranges, validates the buffer, repairs fixups if needed, and marks bad inodes on corrupt reads.
- `indx_write()` writes an index node through `ntfs_write_bh()`.

## Search and Enumeration

- `hdr_find_e()` performs binary search within one index header and returns the exact match or first greater entry/end entry.
- `indx_find()` descends from root through subnode VBN pointers to find a key, saving the traversal path in `ntfs_fnd`.
- `indx_find_sort()` enumerates entries in sorted B-tree order.
- `indx_find_raw()` enumerates root entries and allocation buffers without sorted traversal, using bitmap bits and resumable offsets.

## Insertion

- `hdr_insert_de()` inserts a directory entry into an index header when space is available.
- `indx_create_allocate()` creates initial `$INDEX_ALLOCATION` and `$BITMAP` attributes.
- `indx_add_allocate()` reuses free index buffers or grows index bitmap/allocation attributes.
- `indx_insert_into_root()` inserts into resident root when possible; otherwise it externalizes entries into a new allocation buffer and converts root into a parent.
- `indx_insert_into_buffer()` splits a full index buffer, promotes a split entry upward, updates bitmap bits, and rolls back critical buffer changes on parent-insertion failure.
- `indx_insert_entry()` is the public insert routine and bumps `indx->version`.

## Deletion and Shrink

- `hdr_delete_de()` removes an entry from one index header.
- `indx_free_children()` recursively frees child index buffers and optionally shrinks tail allocation.
- `indx_get_entry_to_replace()` finds a replacement entry for deleting an internal node entry.
- `indx_delete_entry()` handles leaf deletion, internal deletion with replacement, subtree pruning, reinsertion of separator entries, full tree collapse to an empty resident root, allocation/bitmap removal, and version increment.
- `indx_shrink()` truncates index allocation and bitmap attributes when no used bits remain past a point.

## Directory Metadata Update

`indx_update_dup()` finds a directory entry by filename and updates its duplicated `NTFS_DUP_INFO` fields, writing either the external index buffer or resident MFT record.

## Dependencies

Depends on NTFS runlist, attribute sizing/loading, MFT-record mutation, bitmap helpers, buffer-head I/O, and comparison helpers from NTFS3 core headers. It is called by directory lookup/create/delete/rename paths, `$Secure` handling, and `$Extend` system indexes.

## Research Notes

This file is the NTFS3 B-tree engine. Most correctness risk is around corrupt index validation, split/delete rollback, lazy run loading during unlocked readdir, and maintaining allocation bitmap consistency with on-disk index buffers.
