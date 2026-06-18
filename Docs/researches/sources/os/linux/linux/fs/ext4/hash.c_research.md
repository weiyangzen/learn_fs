# File Research: sources/os/linux/linux/fs/ext4/hash.c

Implements ext4 directory htree filename hashing.

Key behavior:
- Provides TEA, half-MD4, and legacy hash implementations.
- Supports signed and unsigned character variants for legacy, half-MD4, and TEA hashes.
- `__ext4fs_dirhash()`:
  - initializes the default hash seed
  - uses the filesystem hash seed if nonzero
  - dispatches by `hinfo->hash_version`
  - supports encrypted-directory `DX_HASH_SIPHASH` via `fscrypt_fname_siphash()`
  - rejects siphash if the encryption key is unavailable
  - clears the low hash bit and avoids the htree EOF sentinel value
  - fills both major and minor hash outputs
- `ext4fs_dirhash()`:
  - applies Unicode casefolding for casefolded directories when possible
  - permits encrypted casefolding only when the encryption key is available
  - falls back to hashing the opaque byte sequence when casefolding fails or is not applicable

Important interactions:
- Used by htree indexed directory lookup/allocation and by inode placement logic that hashes top-level directory names.
- Integrates with fscrypt for keyed siphash and with Unicode normalization for case-insensitive directories.
