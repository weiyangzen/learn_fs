# File Research: sources/os/linux/linux-stable/fs/crypto/bio.c

This file implements block-device-oriented fscrypt helpers for bio decryption and encrypted zeroout.

Key responsibilities:
- Provides `fscrypt_decrypt_bio()` for decrypting completed read bios into page-cache folios.
- Provides `fscrypt_zeroout_range()` for writing ciphertext that decrypts to zeroes over a contiguous encrypted file range.
- Provides an inline-crypto zeroout path when the inode uses block inline encryption.

Important control flow:
- `fscrypt_decrypt_bio()` iterates all folios in a bio and calls `fscrypt_decrypt_pagecache_blocks()` for each segment.
- `fscrypt_zeroout_range_inline_crypt()` builds write bios over `ZERO_PAGE(0)`, attaches fscrypt bio crypto context, submits with blk crypto, and waits for all completions.
- Non-inline `fscrypt_zeroout_range()`:
  - Computes data-unit size and indices.
  - Allocates up to 16 bounce pages, with the first allocation allowed to block via mempool-backed fscrypt allocation.
  - Encrypts zero pages per data unit into bounce pages.
  - Submits synchronous write bios and reuses the bio until the range is complete.
  - Frees bounce pages and bio on exit.

Dependencies:
- Uses core fscrypt helpers from `crypto.c`.
- Uses inline crypto helpers from other fscrypt files when configured.
- Assumes a single block device through `inode->i_sb->s_bdev`.

Risks and invariants:
- `len` must be nonzero and aligned to data-unit size/file logical block expectations.
- The physical blocks must be contiguous.
- Each data unit uses a different IV, so zeroout must encrypt per data unit instead of writing reusable ciphertext.
- Bio status is converted to errno/blk_status in the appropriate direction.
