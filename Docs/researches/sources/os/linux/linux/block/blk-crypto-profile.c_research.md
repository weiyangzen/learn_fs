# File Research: sources/os/linux/linux/block/blk-crypto-profile.c

## Scope

This file implements generic inline-encryption device profile and keyslot management. It lets storage drivers expose crypto capabilities and provides reusable keyslot allocation, programming, eviction, reprogramming, and capability composition.

## Core APIs and Entry Points

- Profile lifecycle:
  - `blk_crypto_profile_init()`, `devm_blk_crypto_profile_init()`, `blk_crypto_profile_destroy()`, `blk_crypto_register()`.
- Keyslot lifecycle:
  - `blk_crypto_get_keyslot()`, `blk_crypto_put_keyslot()`, `blk_crypto_keyslot_index()`.
  - `__blk_crypto_evict_key()`, `blk_crypto_reprogram_all_keys()`.
- Capability helpers:
  - `__blk_crypto_cfg_supported()`, `blk_crypto_intersect_capabilities()`, `blk_crypto_has_capabilities()`, `blk_crypto_update_capabilities()`.
- Hardware-wrapped key operations:
  - `blk_crypto_derive_sw_secret()`, `blk_crypto_import_key()`, `blk_crypto_generate_key()`, `blk_crypto_prepare_key()`.

## Major State

- `struct blk_crypto_keyslot` stores slot refcount, idle LRU node, hash node, key pointer, and owning profile.
- `struct blk_crypto_profile` owns:
  - profile rwsem and lockdep key,
  - optional device pointer for runtime PM,
  - keyslot array,
  - idle slot list and waitqueue,
  - key hash table,
  - low-level driver ops and capability fields.

## Control Flow

- Profile initialization zeroes the profile, creates a dynamic lock class, initializes the rwsem, and optionally allocates keyslot and hash-table state.
- `blk_crypto_get_keyslot()`:
  - returns immediately if the device has no keyslot concept,
  - first attempts a read-locked lookup and ref grab,
  - otherwise enters hardware section with runtime PM and write lock,
  - waits for idle slots if necessary,
  - programs a slot via driver `keyslot_program`,
  - hashes it by key pointer and removes it from idle LRU.
- `blk_crypto_put_keyslot()` decrements the slot refcount and returns it to idle LRU when the count reaches zero.
- `__blk_crypto_evict_key()` calls driver eviction, warns if the key is still referenced, and unlinks the key from hash state even if eviction errors.
- Hardware-wrapped key helpers validate profile support and delegate under the same runtime-PM/write-lock wrapper.
- Capability intersection clears any parent capability not supported by a child; capability update assumes shrinking is externally synchronized.

## Dependencies

- Driver-provided `struct blk_crypto_ll_ops`.
- Runtime PM, rwsems, waitqueues, spinlocks, hlist/list, kvzalloc/kvmalloc.
- Block integrity check in `blk_crypto_register()` disallows integrity and hardware inline encryption together.

## Risks and Invariants

- Calling into hardware requires the device resumed before taking `profile->lock`, because runtime resume can reprogram keys and interact with the same lock.
- Key identity is pointer-based; upper layers must not free a key before eviction and before I/O using it has completed.
- Slot refs must be zero before eviction; nonzero refs indicate a kernel bug and return `-EBUSY`.
- Drivers that lose keys on reset must call `blk_crypto_reprogram_all_keys()`.
- Devices cannot shrink advertised crypto capabilities while bios relying on old capabilities may still be in flight.
