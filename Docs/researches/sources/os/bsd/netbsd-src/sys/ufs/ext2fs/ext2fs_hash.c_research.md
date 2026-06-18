# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_hash.c

This file implements directory-name hashing for ext3/ext4 HTree indexed directories.

Key public function:
- `ext2fs_htree_hash`: computes major/minor hash values for a name using the requested HTree hash version.

Supported hash algorithms:
- Legacy signed/unsigned hash.
- Half-MD4 signed/unsigned hash.
- TEA signed/unsigned hash.

Key internal helpers:
- `ext2fs_prep_hashbuf`: prepares padded 32-bit word buffers from file names.
- `ext2fs_legacy_hash`: Linux-compatible legacy directory hash.
- `ext2fs_half_md4`: modified half-MD4 transform.
- `ext2fs_tea`: Tiny Encryption Algorithm based hash transform.

Important behavior:
- Name length must be 1..255.
- Major hash has its low collision bit cleared.
- `EXT2_HTREE_EOF << 1` is avoided by reducing to the previous value.
- Optional hash seed overrides the default MD4 initialization constants.

Dependencies:
- `ext2fs_htree.h` for hash version constants.
- `ext2fs_hash.h` for MD4 primitive macros.
- Kernel string/mount/vnode includes.

Design notes:
- Compatibility with Linux HTree hashing is the main concern; changes here directly affect indexed directory lookup interoperability.
