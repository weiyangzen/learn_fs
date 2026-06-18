# File Research: sources/os/linux/linux-stable/fs/crypto/fname.c

This file implements fscrypt filename encryption, decryption, no-key name encoding/decoding, encrypted filename sizing, name matching, SipHash directory hashing, and encrypted dentry revalidation.

Key responsibilities:
- Encrypts plaintext filenames into on-disk encrypted names.
- Decrypts encrypted disk names into user-presentable plaintext when keys are available.
- Encodes no-key names using base64url plus optional SHA-256 abbreviation when keys are unavailable.
- Decodes no-key lookup names back into enough information to find directory entries.
- Matches lookup names against directory entries, including abbreviated long no-key names.
- Provides keyed SipHash for casefolded/encrypted directory hashing.
- Revalidates no-key dentries after encryption keys may have appeared.

Important control flow:
- `fscrypt_fname_encrypt()` pads plaintext to the encrypted length, generates IV index 0, and encrypts in place.
- `fname_decrypt()` decrypts into caller buffer and trims trailing NUL padding with `strnlen()`.
- `__fscrypt_fname_encrypted_size()` enforces minimum 16-byte message length and policy-selected padding.
- `fscrypt_fname_disk_to_usr()`:
  - Passes through `.` and `..`.
  - Rejects too-short encrypted names.
  - Decrypts if the key is present.
  - Otherwise builds `struct fscrypt_nokey_name` with dirhashes, up to 149 ciphertext bytes, and SHA-256 of the remainder if needed, then base64url encodes it.
- `fscrypt_setup_filename()`:
  - Leaves unencrypted or dot names unchanged.
  - Loads encryption info.
  - If key is present, encrypts user plaintext into `fname->disk_name`.
  - If key is absent and lookup is allowed, decodes a no-key name and either sets the full disk name or stores hash/abbreviation data.
  - If key is absent for create-style operations, returns `-ENOKEY`.
- `fscrypt_match_name()` compares direct disk names or verifies abbreviated long no-key names with SHA-256.
- `fscrypt_d_revalidate()` invalidates no-key dentries once the directory key becomes available.

Dependencies:
- Uses IV generation from `crypto.c`.
- Uses key setup/encryption-info helpers from other fscrypt files.
- Uses SHA-256, base64url, SipHash, and skcipher APIs.

Risks and invariants:
- Encrypted filenames shorter than 16 bytes are invalid on disk.
- No-key names are designed to avoid illegal filename characters and stay within `NAME_MAX`.
- SHA-256 is only used for long ciphertext names that cannot fit in full no-key form.
- `DCACHE_NOKEY_NAME` dentries are valid only while the encryption key remains unavailable.
- Callers must release allocations with `fscrypt_free_filename()` or related cleanup paths outside this file.
