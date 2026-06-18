# File Research: sources/os/linux/linux/block/blk-crypto-sysfs.c

## Scope

This file exposes blk-crypto capabilities through `/sys/block/$disk/queue/crypto/`.

## Core APIs

- `blk_crypto_sysfs_register()` creates the `crypto` kobject under a disk queue kobject if the queue has a crypto profile.
- `blk_crypto_sysfs_unregister()` drops that kobject.
- `blk_crypto_sysfs_init()` initializes dynamic encryption-mode attributes at boot.

## Sysfs Surface

- Top-level read-only files:
  - `hw_wrapped_keys` appears only if hardware-wrapped keys are supported and prints `supported`.
  - `raw_keys` appears only if raw keys are supported and prints `supported`.
  - `max_dun_bits` prints `8 * max_dun_bytes_supported`.
  - `num_keyslots` prints `profile->num_slots`.
- `modes/` subdirectory:
  - one read-only file per valid encryption mode,
  - visible only if `profile->modes_supported[mode]` is nonzero,
  - prints the supported data-unit-size bitmask as hex.

## Major State

- `struct blk_crypto_kobj` embeds kobject and profile pointer.
- `struct blk_crypto_attr` wraps sysfs attribute plus a profile-aware show callback.
- Dynamic arrays `__blk_crypto_mode_attrs[]` and `blk_crypto_mode_attrs[]` avoid hard-coding mode filenames.

## Dependencies

- `blk_crypto_modes[]` for mode names.
- `struct blk_crypto_profile` capability fields.
- sysfs/kobject attribute group infrastructure.

## Risks and Invariants

- Mode initialization assumes `BLK_ENCRYPTION_MODE_INVALID == 0` and skips index 0.
- Attribute visibility depends on current profile fields; capability shrinking without upper-layer synchronization has the same risk described in profile management.
- `blk_crypto_sysfs_unregister()` assumes the kobject pointer is either valid or safely accepted by `kobject_put()`.
