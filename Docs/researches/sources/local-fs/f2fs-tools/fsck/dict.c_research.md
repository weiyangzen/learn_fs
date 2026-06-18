# File Research: sources/local-fs/f2fs-tools/fsck/dict.c

## Purpose
Embedded Kazlib dictionary implementation, using a red-black tree. In this tree, keys are ordered by a caller-supplied comparator and nodes carry arbitrary data pointers.

## Active fsck-facing functionality
With `DICT_NODEBUG` defined and many blocks under `FSCK_NOTUSED`, the actively compiled core includes:
- Dictionary initialization and allocator selection:
  - `dict_init`
  - `dict_set_allocator`
  - `dict_free_nodes`
- Lookup and insertion:
  - `dict_lookup`
  - `dict_insert`
  - `dict_alloc_insert`
- Traversal:
  - `dict_first`
  - `dict_last`
  - `dict_next`
  - `dict_prev`
- Duplicates and counts:
  - `dict_allow_dupes`
  - `dict_count`
  - `dict_isempty`
  - `dict_isfull`
  - `dict_contains`
- Node lifecycle/accessors:
  - `dnode_create`
  - `dnode_init`
  - `dnode_destroy`
  - `dnode_get`
  - `dnode_getkey`

## Implementation details
- Uses a sentinel nil node stored inside `dict_t`.
- Insertions are standard red-black tree insertions with left/right rotations.
- Duplicate key behavior is opt-in through `dict_allow_dupes`.
- Default node allocation uses `malloc`/`free`; callers can replace allocator hooks.

## Compiled-out sections
Large parts are guarded by `FSCK_NOTUSED`, including:
- dynamic `dict_create` / `dict_destroy`
- delete operations
- lower/upper bound
- sorted bulk load
- merge
- interactive test program under `KAZLIB_TEST_MAIN`

## Dependencies
- Includes `dict.h`.
- Includes `f2fs_fs.h` for the `UNUSED` macro used in allocator signatures.

## Research notes
This is vendored third-party utility code rather than F2FS-specific logic. The header declares a larger API than fsck actually compiles unless build flags enable `FSCK_NOTUSED` or debug/test modes, so new call sites should verify that a function is linked in the normal fsck build.
