# File Research: sources/os/linux/linux-stable/fs/crypto/crypto.c

This file implements core fscrypt content encryption/decryption operations, IV generation, bounce-page allocation, initialization, and logging.

Key responsibilities:
- Maintains the fscrypt read-decryption workqueue.
- Maintains a mempool-backed bounce-page pool for ciphertext pages.
- Provides IV generation for supported fscrypt policy flags.
- Encrypts/decrypts single data units using the kernel skcipher API.
- Encrypts page-cache folio blocks into bounce pages for writeback.
- Decrypts page-cache folio blocks after reads.
- Provides in-place encrypt/decrypt helpers for arbitrary filesystem blocks.
- Initializes fscrypt global caches and keyring support.

Important control flow:
- `fscrypt_generate_iv()` zeroes the IV and then applies policy-specific construction:
  - `IV_INO_LBLK_64` combines inode number and logical index.
  - `IV_INO_LBLK_32` uses hashed inode plus index.
  - `DIRECT_KEY` copies file nonce.
  - Always stores final index little-endian in `iv->index`.
- `fscrypt_crypt_data_unit()` builds one-entry scatterlists for source/destination pages and invokes encrypt or decrypt.
- `fscrypt_encrypt_pagecache_blocks()` validates locked non-large folio and alignment, allocates a bounce page, encrypts each data unit, and stores the source folio in page private metadata.
- `fscrypt_decrypt_pagecache_blocks()` validates locked folio and alignment, then decrypts each data unit in place.
- `fscrypt_initialize()` lazily creates the bounce-page pool only for filesystems that need bounce pages.
- `fscrypt_init()` creates a high-priority unbound read workqueue, an inode-info cache, and fscrypt keyring state.

Dependencies:
- Depends on `fscrypt_private.h`, crypto skcipher API, mempool, and keyring initialization from another fscrypt file.
- Exported helpers are consumed by filesystem writeback/read paths and `bio.c`.

Risks and invariants:
- Data-unit length must be positive and aligned to `FSCRYPT_CONTENTS_ALIGNMENT`.
- Page-cache encryption assumes locked, non-large folios.
- Bounce page allocation requires filesystems to advertise `needs_bounce_pages`.
- In-place block helpers reject filesystems that support sub-block data units.
- Initialization uses acquire/release ordering around the global bounce-page pool pointer.
