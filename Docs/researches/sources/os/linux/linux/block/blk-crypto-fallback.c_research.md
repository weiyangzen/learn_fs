# File Research: sources/os/linux/linux/block/blk-crypto-fallback.c

## Scope

This file implements the blk-crypto software fallback using the kernel crypto API when hardware inline encryption does not support a raw-key configuration.

## Core APIs and Entry Points

- `blk_crypto_fallback_bio_prep()` prepares encrypted bios for fallback processing.
- `blk_crypto_fallback_start_using_mode()` lazily initializes fallback infrastructure and preallocates crypto transforms for a mode.
- `blk_crypto_fallback_evict_key()` evicts a fallback key through the shared crypto profile keyslot manager.
- Internal keyslot ops:
  - `blk_crypto_fallback_keyslot_program()`, `blk_crypto_fallback_keyslot_evict()`.
- Write path:
  - `blk_crypto_fallback_encrypt_bio()`, `__blk_crypto_fallback_encrypt_bio()`, `blk_crypto_alloc_enc_bio()`, `blk_crypto_fallback_encrypt_endio()`.
- Read path:
  - `blk_crypto_fallback_decrypt_endio()`, `blk_crypto_fallback_decrypt_bio()`, `__blk_crypto_fallback_decrypt_bio()`.

## Major State

- Module parameters:
  - `num_prealloc_bounce_pg`, `num_keyslots`, `num_prealloc_fallback_crypt_ctxs`.
- Fallback pools:
  - `bio_fallback_crypt_ctx_pool/cache`, `blk_crypto_bounce_page_pool`, `enc_bio_set`.
- Fallback keyslots:
  - `blk_crypto_keyslots[]` stores current mode and one skcipher tfm per supported mode.
  - `blk_crypto_fallback_profile` exposes fallback as a synthetic crypto profile.
- `blk_crypto_wq` runs read decryption in process context.
- `tfms_init_lock` and `tfms_inited[]` serialize lazy transform setup.
- `blank_key` is random bytes used to clear evicted tfm keys.

## Control Flow

- Fallback initialization creates an encrypted-bio bioset, synthetic crypto profile, workqueue, keyslot array, bounce-page pool, and fallback context mempool.
- Starting a mode allocates a sync skcipher transform for every fallback keyslot and publishes readiness with release/acquire ordering.
- For fallback writes, the original bio is consumed:
  - keyslot is obtained,
  - one or more encrypted bios are allocated,
  - source data units are encrypted into bounce pages using DUN-derived IVs,
  - encrypted bios are submitted,
  - completions free bounce pages and complete the source bio only after all encrypted bios finish.
- For fallback reads, `bi_private` and `bi_end_io` are wrapped. On successful I/O completion, decryption is queued to `blk_crypto_wq`, performed in place, then the original endio/private fields are restored.
- `blk_crypto_fallback_bio_prep()` clears the bio crypto context before submitting fallback reads so lower layers see ordinary bios.

## Dependencies

- Crypto API: `crypto_sync_skcipher`, skcipher requests, scatterlists.
- Generic blk-crypto profile/keyslot manager in `blk-crypto-profile.c`.
- Bio allocation, bvec iteration, cgroup association cloning, mempools, workqueues.

## Risks and Invariants

- Callers must call `blk_crypto_start_using_key()` before data path use; otherwise `tfms_inited[]` may be false and the bio fails.
- Fallback supports raw keys, not hardware-wrapped keys.
- Data segment length and offset must be aligned to the crypto data unit size.
- Write fallback can split one source bio into multiple encrypted bios; source completion depends on correct `__bi_remaining` accounting.
- The temporary page-pointer array is stored inside encrypted bio bvec memory; this relies on `PAGE_PTRS_PER_BVEC > 1`.
- Crypto transform allocation is kept out of the data path to avoid allocation deadlocks.
