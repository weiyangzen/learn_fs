# File Research: sources/os/linux/linux/fs/ubifs/crypto.c

Read completely: 97 lines.

This file integrates UBIFS with fscrypt. It supplies the filesystem encryption operations, stores encryption contexts as UBIFS xattrs, checks encrypted-directory emptiness, and encrypts/decrypts UBIFS data-node payloads in place.

Main entry points: `ubifs_encrypt`, `ubifs_decrypt`, and `ubifs_crypt_operations`.

Key behavior: `ubifs_encrypt` records the pre-encryption compressed length in `dn->compr_size`, pads the data area to `UBIFS_CIPHER_BLOCK_SIZE`, zero-fills padding, and calls `fscrypt_encrypt_block_inplace`. `ubifs_decrypt` validates `compr_size`, decrypts the full encrypted payload length, and returns the original compressed length to the caller.

Important interactions: `dir.c` uses fscrypt preparation APIs for lookup/create/link/rename/readdir names and calls `ubifs_check_dir_empty` through the fscrypt empty-dir hook. `file.c` decrypts data nodes before decompression and encrypts data after compression through the journal write path.

Reliability notes: decrypt-side validation rejects zero, oversized, or buffer-exceeding compressed sizes. Encryption assumes the caller allocated enough space for block padding and asserts that invariant.
