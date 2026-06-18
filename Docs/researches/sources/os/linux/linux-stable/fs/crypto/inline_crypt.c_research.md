# File Research: sources/os/linux/linux-stable/fs/crypto/inline_crypt.c

## Summary
Implements fscrypt integration with blk-crypto inline encryption. It selects inline encryption when policy, mode, mount options, data-unit size, key type, and all block devices support it; prepares and evicts blk-crypto keys; derives software secrets from hardware-wrapped keys; assigns bio crypto contexts; and checks mergeability, direct I/O support, and DUN wrap limits.

## Main Responsibilities
- Discover filesystem block devices through `s_cop->get_devices` or fall back to `sb->s_bdev`.
- Compute required DUN byte width for DIRECT_KEY, IV_INO_LBLK, and default IV strategies.
- Select inline encryption only for regular-file contents encryption with a blk-crypto-capable mode and `SB_INLINECRYPT`.
- Initialize `struct blk_crypto_key` objects and start using them on every filesystem block device.
- Evict blk-crypto keys from block devices and free them securely.
- Ask hardware to derive a software secret from a hardware-wrapped key for non-contents KDF use.
- Generate DUN arrays from fscrypt IVs and attach them to bios.
- Determine whether encrypted data can be merged into an existing bio.
- Report whether direct I/O is supported for an encrypted inode.
- Limit I/O block counts to avoid `IV_INO_LBLK_32` DUN wraparound within a bio.

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
Inline encryption is selected only for regular-file contents, only if the mode maps to blk-crypto, only if the filesystem is mounted with `inlinecrypt`, and only if every backing block device supports the requested mode, data-unit size, DUN width, and key type.

For `IV_INO_LBLK_32`, inline encryption is disabled when filesystem block size differs from page size because some filesystem paths check crypto mergeability only for the first block in a page. Hardware-wrapped keys require inline encryption for file contents; if no suitable inline-crypto capability exists, setup fails.

Bio mergeability compares both crypto key pointer identity and DUN contiguity. `fscrypt_limit_io_blocks()` prevents rare DUN wrap cases from being submitted as one logically contiguous I/O.

## Research Notes
The core external dependency is the block layer's blk-crypto API. Filesystems must call `fscrypt_set_bio_crypt_ctx()` before adding pages and respect `fscrypt_mergeable_bio()` or equivalent DUN-contiguity limits.
