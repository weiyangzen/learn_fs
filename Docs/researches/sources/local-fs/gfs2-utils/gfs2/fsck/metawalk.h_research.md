# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/metawalk.h

## Purpose
Declares the metadata walking API, callback return codes, inode pointer helper type, and `struct metawalk_fxns` callback table.

## Main Elements
- Directory constants: `DIR_LINEAR`, `DIR_EXHASH`.
- Public walkers: `check_inode_eattr()`, `check_metatree()`, `check_leaf_blks()`, `check_dir()`, `check_linear_dir()`, and `check_leaf()`.
- Bitmap/duplicate helpers: `_fsck_bitmap_set()`, `check_n_fix_bitmap()`, `dupfind()`, and `fsck_system_inode()`.
- Macros: `fsck_bitmap_set()` and `fsck_bitmap_set_noino()` add callsite metadata; `iptr_*` macros decode indirect pointer positions.
- `enum meta_check_rc`: `META_ERROR`, `META_IS_GOOD`, `META_SKIP_FURTHER`, `META_SKIP_ONE`.
- `struct iptr`: current inode, buffer, and offset for indirect pointer callbacks.
- `struct metawalk_fxns`: pass-specific callbacks for leaves, metadata, data, EA indirect/leaf/entry/extentry, hash tables, leaf repair, undo, delete, and large-file progress.

## Dependencies And Integration
Includes `util.h` and is the primary contract between generic traversal in `metawalk.c` and pass-specific policy in pass1/pass1b/later passes.

## Risk Notes
The header exposes a broad callback interface where return-code semantics control whether fsck continues, skips, repairs, or deletes. The `is_duplicate(dblock)` macro appears inconsistent with the declared `dupfind(struct fsck_cx *, uint64_t)` signature and would be unsafe if used as written.
