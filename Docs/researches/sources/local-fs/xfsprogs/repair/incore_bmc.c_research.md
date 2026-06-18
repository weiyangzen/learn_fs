# File Research: sources/local-fs/xfsprogs/repair/incore_bmc.c

## Role

`incore_bmc.c` initializes bmap btree cursors used during inode bmap btree validation.

## Function

`init_bm_cursor`:

- Clears the cursor.
- Sets inode to `NULLFSINO`.
- Records number of levels.
- Initializes every level’s block and sibling pointers to `NULLFSBLOCK`.
- Initializes first/last keys to `NULLFILEOFF`.

## Interactions

The cursor is used by bmap btree scanning code to validate key ordering, sibling pointers, and parent/child key consistency while processing inode data or attr forks.
