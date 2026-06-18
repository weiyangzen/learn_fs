# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_hash.c

This file implements ext2 htree directory name hashing compatible with Linux indexed directories. It supports legacy, TEA, and half-MD4 hash algorithms, including signed and unsigned character variants.

Key responsibilities:
- Implement the half-MD4 transform used by ext directory indexes.
- Implement TEA-based hashing.
- Implement legacy ext2 directory hash.
- Prepare padded hash input buffers using signed or unsigned character interpretation.
- Normalize and return major/minor htree hash values.

Important functions:
- `ext2_half_md4`: MD4-derived transform over 8-word data blocks.
- `ext2_tea`: TEA-style transform for directory hashing.
- `ext2_legacy_hash`: Older ext2 hash algorithm.
- `ext2_prep_hashbuf`: Packs filename bytes into 32-bit words with length-derived padding.
- `ext2_htree_hash`: Public dispatcher. Validates name length, applies optional hash seed, selects algorithm/version, clears the low collision bit in the major hash, avoids EOF sentinel collision, and returns major/minor hashes.

Important interactions:
- Used by `ext2_htree.c` for htree lookup, directory block splitting, and index creation.
- Hash version constants and structures come from `htree.h`.

Notable behavior:
- Invalid names or unknown hash versions return `-1` and zero output hashes.
- The major hash low bit is reserved for collision handling and is cleared before return.
