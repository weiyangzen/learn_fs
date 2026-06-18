# File Research: sources/os/linux/linux/fs/crypto/inline_crypt.c

## Summary
Implements fscrypt integration with blk-crypto inline encryption. It decides whether a regular file can use inline encryption, prepares and evicts blk-crypto keys, derives software secrets from hardware-wrapped keys, assigns bio crypto contexts, checks bio mergeability, gates direct I/O support, and limits I/O to avoid data-unit-number wraparound.

## Main Responsibilities
- Discover block devices used by a filesystem, using `s_cop->get_devices` when available.
- Compute the number of DUN bytes required by the inode’s IV generation policy.
- Select inline encryption when the file, mode, mount options, policy, data-unit size, and all block devices support it.
- Initialize `struct blk_crypto_key` objects and start using them on all filesystem block devices.
- Evict blk-crypto keys during prepared-key destruction.
- Ask inline-encryption hardware to derive software secrets from hardware-wrapped keys.
- Generate DUN arrays from fscrypt IVs and attach them to bios.
- Determine whether a bio can merge additional encrypted data.
- Report whether encrypted DIO is supported for an inode.
- Limit I/O block counts for `IV_INO_LBLK_32` DUN wraparound.

## Key APIs
- `fscrypt_select_encryption_impl()`
- `fscrypt_prepare_inline_crypt_key()`
- `fscrypt_destroy_inline_crypt_key()`
- `fscrypt_derive_sw_secret()`
- `__fscrypt_inode_uses_inline_crypto()`
- `fscrypt_set_bio_crypt_ctx()`
- `fscrypt_mergeable_bio()`
- `fscrypt_dio_supported()`
- `fscrypt_limit_io_blocks()`

## Important Behavior
Inline encryption is selected only for regular-file contents encryption, only when the fscrypt mode has a blk-crypto equivalent, and only when the filesystem is mounted with `SB_INLINECRYPT`. For `IV_INO_LBLK_32`, inline encryption is disabled when filesystem block size differs from page size because some filesystem code only checks mergeability for the first block in a page.

Hardware-wrapped keys require inline encryption for file contents. The software secret derived from hardware is used for non-contents KDF needs, while the wrapped key itself is passed to blk-crypto for actual contents encryption.

Bio mergeability compares both crypto key pointer identity and DUN contiguity. `fscrypt_limit_io_blocks()` handles the rare case where `IV_INO_LBLK_32` would wrap within a logically contiguous I/O.

## Research Notes
The core dependency is the block layer’s blk-crypto API. Correctness depends on each filesystem calling `fscrypt_set_bio_crypt_ctx()` before adding pages and honoring `fscrypt_mergeable_bio()` or equivalent DUN-contiguity limits.
