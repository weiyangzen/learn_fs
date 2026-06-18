# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_hash.c

This file implements ext2/ext3/ext4 directory HTree hash algorithms compatible with Linux indexed directories.

Key responsibilities:
- Provide half-MD4, TEA, and legacy directory name hashing.
- Support signed and unsigned character variants.
- Prepare padded hash input buffers in Linux-compatible form.
- Apply filesystem hash seeds when present.
- Normalize major hash values for HTree ordering and EOF collision avoidance.

Important functions:
- `ext2_half_md4`: Modified half-MD4 transform used by Linux dirindex.
- `ext2_tea`: Tiny Encryption Algorithm based hash transform.
- `ext2_legacy_hash`: Original ext2 legacy name hash.
- `ext2_prep_hashbuf`: Converts name bytes into padded 32-bit hash words.
- `ext2_htree_hash`: Public dispatcher for `EXT2_HTREE_TEA`, `LEGACY`, `HALF_MD4`, and unsigned variants; returns major/minor hash values.

Important interactions:
- Called by `ext2_htree.c` to find leaves, split directory blocks, create indexes, and add indexed entries.
- Uses HTree constants from `htree.h` and trace probes for unexpected hash versions.

Notable behavior:
- Returns `-1` and zeroes output hashes for invalid names or unsupported hash versions.
- Clears the low collision bit in the major hash and avoids the HTree EOF sentinel value.
