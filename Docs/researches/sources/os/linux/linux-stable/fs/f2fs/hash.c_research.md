# File Research: sources/os/linux/linux-stable/fs/f2fs/hash.c

`hash.c` computes F2FS directory-entry name hashes. It uses the ext3-derived TEA hash for ordinary byte-string names and fscrypt SipHash for encrypted casefolded plaintext names.

`TEA_transform()` and `str2hashbuf()` implement the legacy TEA block transform and filename block packing. `TEA_hash_name()` initializes the fixed hash seed, hashes the name in 16-byte chunks, and clears `F2FS_HASH_COL_BIT` from the returned hash.

`f2fs_hash_filename()` is the exported entry point. It requires `fname->disk_name`, returns hash zero for `.` and `..`, and normally hashes the on-disk name. For casefolded directories it prefers the normalized casefolded name; if the name is not valid Unicode it falls back to the user plaintext name. For encrypted casefolded directories it hashes the plaintext qstr with `fscrypt_fname_siphash()` so lookup remains stable across ciphertext names.

This file depends on filename preparation in `dir.c`, Unicode casefold support, and fscrypt. The key invariant is that the hash must match the lookup name semantics: bytewise for ordinary directories, normalized plaintext for casefolded directories, and fscrypt-safe SipHash when encryption and casefolding combine.
