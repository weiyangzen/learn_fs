# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_super.c

Superblock helper implementation. It validates core superblock fields, reads/writes the primary superblock, handles metadata checksums, computes group counts and last-group sizes, and determines sparse-super/group-descriptor metadata placement.

Key behavior:
- `ext4_block_group_cnt`, `ext4_blocks_in_group_cnt`, and `ext4_inodes_in_group_cnt` compute total and per-group counts with last-group adjustment.
- `ext4_sb_csum`, `ext4_sb_set_csum`, and `ext4_sb_verify_csum` implement metadata-csum superblock CRC32C over fields before the checksum.
- `ext4_sb_write` updates checksum before writing 1024 bytes at the ext superblock offset.
- `ext4_sb_check` validates magic, nonzero counts, inode size, first inode, descriptor size bounds, and checksum.
- `ext4_sb_sparse` implements the ext sparse-super rule: groups 0/1 and powers of 3, 5, or 7.
- `ext4_bg_num_gdb` handles descriptor backup counts with and without `meta_bg`.
- `ext4_num_base_meta_clusters` estimates base metadata clusters for a block group.

Notable dependencies:
- Uses inline feature/count helpers from `include/ext4_super.h`.
- CRC32C comes from `ext4_crc32`.
- Block IO is provided by `ext4_blockdev`.

Research notes:
- `ext4_num_base_meta_clusters` shifts by `log_cluster_size` after computing a block-count expression; because `log_cluster_size` is a log2 block-size field, this deserves scrutiny for bigalloc-style calculations.
- Superblock checksum validation only applies when `metadata_csum` is present.
