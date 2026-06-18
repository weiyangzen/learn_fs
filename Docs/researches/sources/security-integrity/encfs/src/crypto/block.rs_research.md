## sources/security-integrity/encfs/src/crypto/block.rs

Purpose: Block-layout and per-block encryption/decryption abstraction for EncFS file data. It supports legacy EncFS block format with optional MAC prefix and V7 AES-GCM-SIV authenticated block mode.

Important APIs and types: constants `AES_GCM_SIV_BLOCK_TAG_BYTES` and `LEGACY_MAX_BLOCK_MAC_BYTES`, enum `BlockMode`, `BlockMode::from_config`, `overhead_bytes`, struct `BlockLayout` with size conversion helpers, and `BlockCodec` with `decrypt_block`/`encrypt_block` plus legacy and AES-GCM-SIV internals.

Control flow: `BlockLayout` validates block size exceeds overhead and maps physical/logical sizes. `BlockCodec::decrypt_block` treats all-zero sparse blocks as zeros when `allow_holes`, then dispatches by mode. Legacy decrypt calls `SslCipher::legacy_decrypt_block_inplace`, verifies a computed 64-bit MAC prefix unless ignored, and returns plaintext. AES-GCM-SIV decrypt splits tag/ciphertext and verifies via cipher. Encrypt performs the inverse, prepending MAC/tag and encrypting payload.

State and persistence: Defines on-disk block shape and authentication bytes. Dependencies include `SslCipher` methods and `ConfigType`. Integration is consumed by `crypto/file.rs` and config validation. Risks include sentinel selection of AES-GCM-SIV by V7 plus 16-byte MAC, strict MAC failures on corrupted legacy data, and sparse-hole zero-block special casing. Unit-level test coverage is largely through file codec tests.
