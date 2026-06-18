# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/dirhash.c

Implements ext2/ext4 directory filename hashing for htree indexes. It supports legacy, half-MD4, and TEA hash variants, with signed and unsigned character modes.

Core helpers:
- `TEA_transform`: keyed 32-bit TEA-based Davis-Meyer transform.
- `halfMD4Transform`: cut-down MD4 transform returning hash state.
- `dx_hack_hash`: old legacy directory hash.
- `str2hashbuf`: packs filename bytes into 32-bit words with length-based padding.

APIs:
- `ext2fs_dirhash`: hashes raw filename bytes with optional seed.
- `ext2fs_dirhash2`: optionally casefolds/normalizes through an `ext2fs_nls_table` before calling `ext2fs_dirhash`.

Behavior:
- All-zero seed uses the default MD4 initialization constants.
- Unsupported hash versions return `EXT2_ET_DIRHASH_UNSUPP`.
- Returned primary hash has its low bit cleared.
- Minor hash is returned for hash versions that produce one.
- `ext2fs_dirhash2` falls back to opaque byte hashing if casefolding returns `-EINVAL`.

Implementation notes:
- Casefolding uses a fixed `PATH_MAX` stack buffer.
- The function itself does not perform normalization unless `ext2fs_dirhash2` is used with charset and `EXT4_CASEFOLD_FL`.
