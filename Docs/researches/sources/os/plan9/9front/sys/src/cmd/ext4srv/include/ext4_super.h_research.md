# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_super.h

Superblock accessor and validation API header.

Key behavior:
- Provides inline getters/setters for 64-bit block counts and free block counts.
- Provides inline block size and descriptor size helpers.
- Provides inline checks for superblock flags, compatible features, incompatible features, read-only-compatible features, flex group ID/size, and first meta block group.
- Declares group-count, per-group block/inode count, superblock read/write/check, sparse-super presence, group descriptor backup count, base metadata cluster count, and checksum setter functions.

Notable dependencies:
- Includes `ext4_types.h` and `ext4_misc.h`.
- Implemented by `ext4_super.c`; used throughout ext4srv.

Research notes:
- Descriptor size is clamped upward to the 32-byte minimum, while full validation rejects sizes above the 64-byte maximum.
- Feature check helpers return boolean results from bit tests on little-endian on-disk fields.
