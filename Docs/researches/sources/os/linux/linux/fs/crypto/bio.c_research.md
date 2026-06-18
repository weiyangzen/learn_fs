# File Research: sources/os/linux/linux/fs/crypto/bio.c

## Purpose
Provides block-device fscrypt helpers for decrypting read bios and writing encrypted zeroes to ranges of encrypted files.

## Main Elements
- `fscrypt_decrypt_bio()`: iterates all folios in a completed read bio and decrypts pagecache blocks, setting `bio->bi_status` on failure.
- Inline-crypto zeroout: `fscrypt_zeroout_range_inline_crypt()` builds bios of `ZERO_PAGE()` segments, attaches fscrypt bio crypto contexts, submits via `blk_crypto_submit_bio()`, and waits for all completions.
- Completion support: `struct fscrypt_zero_done`, `fscrypt_zeroout_range_done()`, and end_io callback aggregate async write status.
- Software zeroout: `fscrypt_zeroout_range()` encrypts zero data units into bounce pages, writes them via synchronous bios, and reuses allocated pages in batches.
- Exported symbols: `fscrypt_decrypt_bio()` and `fscrypt_zeroout_range()`.

## Dependencies And Integration
Integrates fscrypt content crypto from `crypto.c`, block bios, blk-crypto inline contexts, filesystem block-device `s_bdev`, and bounce-page allocation.

## Risk Notes
Zeroout must write ciphertext that decrypts to zero per data unit; it cannot simply write identical ciphertext blocks because IVs differ. The helper assumes contiguous logical/physical blocks and a single block device. Inline and software paths have different submission/completion behavior.
