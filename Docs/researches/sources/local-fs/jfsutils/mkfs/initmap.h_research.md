# File Research: sources/local-fs/jfsutils/mkfs/initmap.h

Header for mkfs block-map initialization.

Defines flags:
- `ALLOC`
- `FREE`
- `BADBLOCK`

Declares:
- `calc_map_size(...)`
- `markit(...)`
- `record_LVM_BadBlks(...)`
- `verify_last_blocks(...)`
- `write_block_map(...)`

Filesystem relevance: public interface from `mkfs.c`, inode initialization, and bad-block handling into block-map construction.
