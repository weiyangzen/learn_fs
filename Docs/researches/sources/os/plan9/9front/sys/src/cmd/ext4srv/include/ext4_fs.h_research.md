# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_fs.h

Core in-memory filesystem state and filesystem helper API header.

Key behavior:
- `ext4_fs` stores read-only state, block device, superblock, UUID checksum seed, indirect block limits/geometry, last inode allocation group, journal objects, and current transaction.
- Defines block group and inode reference wrappers carrying the loaded block, typed pointer, owning filesystem, index, and dirty flag.
- Provides inline block-address/group-index conversions.
- Declares filesystem init/fini and feature checking.
- Declares group descriptor and inode reference get/put functions.
- Declares inode block initialization, inode allocation/free, truncation, allocation-goal helpers, block mapping/initialization/append, and link-count increment/decrement.

Notable dependencies:
- Includes `ext4_types.h` and `ext4_misc.h`.
- Implemented primarily by `ext4_fs.c`; used by allocation, directory, file IO, mkfs, and journal code.

Research notes:
- `curr_trans` is the bridge used by `ext4_trans.c` to journal metadata dirtying.
- The address conversion helpers account for `first_data_block` in 1 KiB-block filesystems.
