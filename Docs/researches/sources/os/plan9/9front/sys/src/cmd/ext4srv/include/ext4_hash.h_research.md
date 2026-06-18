# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_hash.h

Directory htree hash header.

Key behavior:
- Defines `ext4_hash_info`, carrying major hash, minor hash, hash version, and seed pointer.
- Declares `ext2_htree_hash`, the shared name-hash function for indexed directories.

Notable dependencies:
- Includes `ext4_config.h`.
- Implemented by `ext4_hash.c`; consumed by `ext4_dir_idx.c`.

Research notes:
- The public function name uses the ext2 prefix because ext htree hashing is shared across ext2/3/4 directory-index formats.
