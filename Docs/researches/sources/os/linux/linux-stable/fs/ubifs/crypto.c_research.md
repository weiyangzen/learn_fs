# File Research: sources/os/linux/linux-stable/fs/ubifs/crypto.c

UBIFS fscrypt integration and encrypted data-node payload handling.

Key responsibilities:
- Implements fscrypt context access through UBIFS xattrs:
  - `ubifs_crypt_get_context()`
  - `ubifs_crypt_set_context()`
  - `ubifs_crypt_empty_dir()`
- Encrypts and decrypts UBIFS data-node payloads:
  - `ubifs_encrypt()`
  - `ubifs_decrypt()`
- Publishes `ubifs_crypt_operations`.

Important behavior:
- Encryption context is stored in `UBIFS_XATTR_NAME_ENCRYPTION_CONTEXT`.
- `ubifs_crypt_set_context()` writes the context unlocked because it operates on a new inode that is not yet externally visible.
- `ubifs_encrypt()` records the original compressed payload size in `dn->compr_size`, pads to `UBIFS_CIPHER_BLOCK_SIZE`, zero-fills padding, then calls `fscrypt_encrypt_block_inplace()`.
- `ubifs_decrypt()` validates `dn->compr_size` against `UBIFS_BLOCK_SIZE` and the caller-provided encrypted data length, decrypts in place, then returns the original compressed length through `out_len`.

Cross-file links:
- `dir.c` prepares encrypted names, symlinks, and new inode contexts.
- `file.c` calls `ubifs_decrypt()` before decompression and bulk-read population.
- `compress.c` receives the post-decryption compressed length.

Invariants and risks:
- `compr_size` is meaningful for encrypted data nodes: it preserves compressed length across cipher-block padding.
- Bad `compr_size` returns `-EINVAL` and protects decompression from padded/corrupt lengths.
- Uses `virt_to_page()` and `offset_in_page()` for in-place encryption/decryption, so the payload storage must remain page-backed and valid.
