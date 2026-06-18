# File Research: sources/os/linux/linux/block/blk-crypto-internal.h

## Scope

This internal header defines blk-crypto mode metadata, shared crypto helpers for bio/request merge and request lifecycle, sysfs declarations, fallback declarations, and compile-time stubs when inline encryption or fallback is disabled.

## Major Types and Declarations

- `struct blk_crypto_mode` describes each encryption mode’s display name, crypto API cipher string, key size, security strength, and IV size.
- `blk_crypto_modes[]` is declared for mode metadata.
- Inline-encryption declarations include:
  - sysfs register/unregister,
  - DUN increment and mergeability helpers,
  - keyslot get/put and eviction,
  - config support check,
  - ioctl dispatch.

## Core Helpers

- Merge checks:
  - `bio_crypt_ctx_back_mergeable()`, `bio_crypt_ctx_front_mergeable()`, `bio_crypt_ctx_merge_rq()`.
- Request state:
  - `blk_crypto_rq_set_defaults()`, `blk_crypto_rq_is_encrypted()`, `blk_crypto_rq_has_keyslot()`.
  - `blk_crypto_rq_get_keyslot()`, `blk_crypto_rq_put_keyslot()`, `blk_crypto_free_request()`.
  - `blk_crypto_rq_bio_prep()`.
- Bio state:
  - `bio_crypt_advance()`, `bio_crypt_free_ctx()`, `bio_crypt_do_front_merge()`.
- Fallback:
  - `blk_crypto_fallback_bio_prep()`, `blk_crypto_fallback_start_using_mode()`, `blk_crypto_fallback_evict_key()`.

## Dependencies

- Public `bio`, `blk-mq`, and blk-crypto types.
- `CONFIG_BLK_INLINE_ENCRYPTION` and `CONFIG_BLK_INLINE_ENCRYPTION_FALLBACK` determine whether helpers compile to real declarations or harmless stubs.

## Risks and Invariants

- Front merge must copy the incoming bio’s DUN into the request crypt context when inline encryption is enabled.
- Request crypto cleanup assumes keyslots are released before freeing request crypto context, with a warning fallback.
- Disabled inline encryption makes merge checks return true and crypto ioctl return `-ENOTTY`, preserving callers without crypto behavior.
