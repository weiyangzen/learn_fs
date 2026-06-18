# File Research: sources/os/linux/linux-stable/fs/ext4/hash.c

This file implements ext4 directory-entry hash calculation for htree indexed directories.

Major responsibilities:
- Hash algorithms:
  - Legacy signed and unsigned dx hash via `dx_hack_hash_signed()` / `dx_hack_hash_unsigned()`.
  - Half-MD4 transform via `half_md4_transform()`.
  - TEA transform via `TEA_transform()`.
  - SipHash for encrypted/casefold-aware directory names when the fscrypt key is available.
- String packing:
  - `str2hashbuf_signed()` and `str2hashbuf_unsigned()` pack filename bytes into 32-bit words with length-based padding.
- Core hash selection:
  - `__ext4fs_dirhash()` initializes default or supplied hash seed, switches by `hinfo->hash_version`, computes major and minor hash values, clears the low bit of the major hash, and avoids the htree EOF sentinel.
- Public entry point:
  - `ext4fs_dirhash()` optionally casefolds names with the superblock unicode map for casefolded directories before hashing, provided encryption state permits it.

Important design points:
- Seeds allow per-filesystem hash uniqueness; all-zero seed falls back to built-in defaults.
- Signed and unsigned variants preserve compatibility with historical directory hash behavior.
- SipHash requires the directory encryption key; without it the function warns and returns `-EINVAL`.
- Casefolding allocates a `PATH_MAX` buffer, hashes the folded name if conversion succeeds, and falls back to opaque byte hashing if unicode casefolding fails.
- The returned major hash always has its low bit cleared, matching htree split conventions.

Key invariants:
- Hash version validation is centralized in `__ext4fs_dirhash()`.
- `len == 0` and `name == NULL` can be used by callers to test hash-version support.
- Minor hash is zero for 32-bit-only hash variants and populated for half-MD4/TEA/SipHash.
