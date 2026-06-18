# File Research: sources/os/linux/linux/block/blk-crypto.c

## Scope

This file implements blk-crypto bio/request context handling, supported encryption mode definitions, key initialization, native-vs-fallback decision logic, key eviction, and user ioctls for hardware-wrapped key operations.

## Core APIs and Entry Points

- Mode and context setup:
  - `blk_crypto_modes[]`.
  - `bio_crypt_set_ctx()`, `__bio_crypt_free_ctx()`, `__bio_crypt_clone()`.
  - `blk_crypto_init_key()`.
- DUN/merge helpers:
  - `bio_crypt_dun_increment()`, `__bio_crypt_advance()`, `bio_crypt_dun_is_contiguous()`.
  - `bio_crypt_rq_ctx_compatible()`, `bio_crypt_ctx_mergeable()`.
- Request integration:
  - `__blk_crypto_rq_get_keyslot()`, `__blk_crypto_rq_put_keyslot()`, `__blk_crypto_free_request()`, `__blk_crypto_rq_bio_prep()`.
- Submission/configuration:
  - `__blk_crypto_submit_bio()`.
  - `blk_crypto_config_supported_natively()`, `blk_crypto_config_supported()`, `blk_crypto_start_using_key()`.
  - `blk_crypto_evict_key()`.
- Ioctls:
  - `blk_crypto_ioctl()` dispatches import/generate/prepare wrapped-key commands.

## Major State

- Supported modes include AES-256-XTS, AES-128-CBC-ESSIV, Adiantum, and SM4-XTS with cipher strings, key sizes, security strengths, and IV sizes.
- `bio_crypt_ctx_cache` and `bio_crypt_ctx_pool` allocate bio/request crypto contexts.
- Module parameter `num_prealloc_crypt_ctxs` sizes the context mempool.

## Control Flow

- `bio_crypt_ctx_init()` creates the context cache/mempool and validates mode definitions at boot.
- Bio crypto contexts hold a key pointer and DUN array. Advancing a bio increments the DUN by data units.
- Mergeability requires matching key pointer and contiguous DUN sequence.
- `__blk_crypto_submit_bio()` fails encrypted bios with no data; if native support is absent, it uses fallback when enabled and the key type is supported.
- `blk_crypto_start_using_key()` must be called by upper layers before I/O to ensure native support or preallocated fallback transforms.
- `blk_crypto_evict_key()` evicts from native profile or fallback, logs errors, and returns void because callers cannot recover meaningfully.
- Wrapped-key ioctls copy arguments from userspace, validate reserved fields and sizes, call profile operations, copy generated material back, and zero temporary key buffers.

## Dependencies

- `blk-crypto-profile.c` for profiles, keyslots, and wrapped-key operations.
- `blk-crypto-fallback.c` for software fallback.
- Bio and request crypto hooks from `blk-crypto-internal.h`.
- Userspace ABI structures and ioctl numbers from public blk-crypto headers.

## Risks and Invariants

- `bio_crypt_set_ctx()` expects a reclaimable GFP mask so mempool allocation cannot fail.
- Key pointers, not key bytes, define merge/keyslot identity.
- DUN wraparound is not treated as contiguous.
- Fallback only supports raw keys; hardware-wrapped keys require native hardware support.
- ioctl paths must zero stack key buffers on all exits, which this file does with `memzero_explicit()`.
