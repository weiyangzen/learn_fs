# File Research: sources/os/linux/linux/fs/crypto/crypto.c

## Purpose
Implements fscrypt content encryption/decryption primitives, bounce-page allocation, IV generation, read-decrypt workqueue setup, initialization, and logging.

## Main Elements
- Global resources: preallocated bounce-page mempool, high-priority unbound read workqueue, fscrypt inode-info slab cache, and init mutex.
- Workqueue: `fscrypt_enqueue_decrypt_work()` queues read-decrypt work.
- Bounce pages: `fscrypt_alloc_bounce_page()` and `fscrypt_free_bounce_page()` allocate/free ciphertext pages from a mempool and store original folio pointers in page private data.
- IV generation: `fscrypt_generate_iv()` handles normal IVs, `IV_INO_LBLK_64`, `IV_INO_LBLK_32`, and `DIRECT_KEY` nonce-based modes.
- Data-unit crypto: `fscrypt_crypt_data_unit()` performs skcipher encrypt/decrypt for one data unit with scatterlists and generated IV.
- Pagecache encryption: `fscrypt_encrypt_pagecache_blocks()` encrypts aligned pagecache blocks into a bounce page for writeback.
- In-place crypto: `fscrypt_encrypt_block_inplace()` and `fscrypt_decrypt_block_inplace()` handle filesystem blocks outside the pagecache, rejecting subblock data-unit filesystems.
- Pagecache decryption: `fscrypt_decrypt_pagecache_blocks()` decrypts aligned data units in locked, not-yet-uptodate folios.
- Initialization: `fscrypt_initialize()` lazily creates the bounce-page pool only for filesystems needing it; `fscrypt_init()` allocates the workqueue/slab and initializes the keyring.
- Logging: `fscrypt_msg()` rate-limits fscrypt messages with optional inode context.

## Dependencies And Integration
Used by fscrypt-enabled filesystems, `bio.c`, filename crypto, key setup, and block writeback/read paths. It depends on crypto skcipher APIs, mempools, folios/pages, and fscrypt policy/key state.

## Risk Notes
Alignment to crypto data-unit size is strictly enforced. Bounce-page mempool use is designed to avoid writeback deadlocks, but only the first page can safely use reclaiming allocation. IV generation must stay synchronized with I/O merging limits and policy flags.
