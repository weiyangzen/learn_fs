# File Research: sources/os/linux/linux/fs/qnx4/namei.c

## Role

Implements QNX4 directory lookup.

## Key Functions

- `qnx4_match()` checks one directory entry against a requested name using `get_entry_fname()`.
- `qnx4_find_entry()` scans directory blocks and entries, using `qnx4_block_map()` and `sb_bread()`, and returns the matching buffer plus computed inode number.
- `qnx4_lookup()` resolves link entries to their real inode block/index, loads the inode with `qnx4_iget()`, and returns `d_splice_alias()`.

## Research Notes

The lookup path mirrors readdir's handling of link entries. It does not create or mutate directory entries because the driver is read-only.
