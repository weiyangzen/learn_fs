# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zio_crypt.c

## Purpose

`zio_crypt.c` implements ZFS block encryption and authentication mechanics: key initialization, key wrapping/unwrapping, salt/IV generation, MAC generation, block pointer parameter encoding, ZIL/dnode/object-set special handling, indirect MAC checksums, and ABD wrappers around crypto operations.

## Major Responsibilities

- Defines supported encryption suites in `zio_crypt_table[]`.
- Initializes, destroys, wraps, and unwraps `zio_crypt_key_t`.
- Rotates salts after a configured number of uses.
- Generates random IVs and dedup-derived IV/salt values.
- Performs AES-GCM/AES-CCM encryption and decryption through `zio_do_crypt_uio()`.
- Performs SHA512-HMAC operations.
- Encodes and decodes encryption salt/IV/MAC fields in block pointers and ZIL blocks.
- Authenticates indirect block MAC trees.
- Authenticates objset physical blocks with portable and local MACs.
- Builds UIO layouts for normal blocks, ZIL blocks, and dnode blocks.
- Provides ABD-level crypto wrappers.

## On-Disk Crypt Layout

The file documents where encryption metadata lives:

- Salt: 64 bits in `DVA[2].dva_word[0]`.
- IV: first 64 bits in `DVA[2].dva_word[1]`, remaining 32 bits in the upper `blk_fill` IV field.
- MAC: usually stored in the second half of `blk_cksum`.
- ZIL MAC: stored in the embedded checksum inside `zil_chain_t`.
- Objset blocks: store two 256-bit MACs in `objset_phys_t`.
- Indirect blocks: store checksum-of-child-MACs rather than requiring keys to verify the tree shape.

Encrypted blocks reserve DVA space, which affects copy count decisions elsewhere in the ZIO pipeline.

## Supported Crypt Suites

`zio_crypt_table[]` includes:

- inherit/on/off placeholders
- AES-128/192/256 CCM
- AES-128/192/256 GCM

Authentication uses SHA512-HMAC for object authentication and key-related derivations.

## Key Lifecycle

`zio_crypt_key_init()` creates a new key with random GUID, master key material, HMAC key material, and salt. It derives the current encryption key with HKDF-SHA512 and initializes ICP key structures and optional crypto context templates.

`zio_crypt_key_destroy()` destroys locks/templates and zeroes key memory.

`zio_crypt_key_wrap()` encrypts master/HMAC key material with a wrapping key and authenticates AAD containing GUID, crypt suite, and key version for current-format keys.

`zio_crypt_key_unwrap()` decrypts wrapped key material, generates a fresh runtime salt, derives the current key, initializes key structures/templates, and records crypt metadata.

`zio_crypt_key_get_salt()` returns the current salt and increments usage count. If the count reaches `ZFS_CURRENT_MAX_SALT_USES`, `zio_crypt_key_change_salt()` rotates the salt and current derived key.

## IV and Salt Generation

`zio_crypt_generate_iv()` creates a random 96-bit IV.

`zio_crypt_generate_iv_salt_dedup()` derives salt and IV from an HMAC of plaintext. This allows encrypted dedup to produce identical ciphertext for identical plaintext within a clone family, while not exposing a plaintext hash directly.

## Core Crypto

`zio_do_crypt_uio()` is the low-level encryption/decryption function. It configures AES-CCM or AES-GCM parameters, passes AAD, uses the MAC as the final cipher UIO vector, and returns `ECKSUM` on invalid MAC during decrypt.

`zio_do_crypt_data()` builds UIOs, selects the correct derived key for the provided salt, calls `zio_do_crypt_uio()`, cleans temporary buffers, and stores failed decrypt buffers for debugging.

`zio_do_crypt_abd()` adapts ABD data to linear buffers and calls `zio_do_crypt_data()`.

## Block Pointer Encoding

`zio_crypt_encode_params_bp()` and `zio_crypt_decode_params_bp()` store/recover salt and IV from block pointers, accounting for block pointer byte order.

`zio_crypt_encode_mac_bp()` and `zio_crypt_decode_mac_bp()` store/recover MAC bytes from `blk_cksum` words 2 and 3. Objset blocks are special and return zero MAC here because their MACs are inside the objset payload.

`zio_crypt_encode_mac_zil()` and `zio_crypt_decode_mac_zil()` handle MACs in ZIL embedded checksum fields.

## Authentication Helpers

`zio_crypt_bp_zero_nonportable_blkprop()` masks block pointer fields before authentication so raw send/receive portability works. Version 0 compatibility is preserved for read-only import of old-format pools.

`zio_crypt_bp_auth_init()` constructs a portable authentication buffer containing selected `blk_prop` fields and MAC bytes.

`zio_crypt_bp_do_hmac_updates()`, `zio_crypt_bp_do_indrect_checksum_updates()`, and `zio_crypt_bp_do_aad_updates()` feed that portable block pointer representation into HMAC/SHA/AAD contexts.

## Objset Authentication

`zio_crypt_do_objset_hmacs()` computes two MACs:

- Portable MAC: protects `os_type`, portable `os_flags`, and metadnode fields. This is suitable for raw sends.
- Local MAC: protects non-portable accounting-related state when user/group/project accounting objects are present.

Objset MAC calculations always normalize values to little-endian representation rather than simply using on-disk byte order.

## Indirect MAC Checksums

`zio_crypt_do_indirect_mac_checksum_impl()` computes a SHA512 digest over portable fields and child MACs for all block pointers in an indirect block.

`zio_crypt_do_indirect_mac_checksum()` verifies current format first and falls back to version 0 on checksum mismatch. This allows verification without loading the encryption key.

`zio_crypt_do_indirect_mac_checksum_abd()` adapts ABD buffers.

## ZIL Special Handling

`zio_crypt_init_uios_zil()` encrypts sensitive log-record payloads but leaves `zil_chain_t`, common log record headers, and embedded block pointers in plaintext. Plaintext portions are authenticated as AAD. It parses records up to `zc_nused`, handles byteswapped headers, and creates UIO vectors only for encrypted spans.

## Dnode Special Handling

`zio_crypt_init_uios_dnode()` leaves dnode core fields and block pointers plaintext for scrub/claim visibility while encrypting eligible bonus buffers. It authenticates portable dnode fields, block pointer MAC/properties, spill block pointers, and unencrypted bonus buffers as AAD.

`zio_crypt_copy_dnode_bonus()` copies encrypted bonus-buffer data from an ABD into a destination buffer at matching dnode offsets.

## Normal Block Handling

`zio_crypt_init_uios_normal()` creates a simple plaintext vector and ciphertext vector plus MAC vector. It is used for most encrypted object types.

`zio_crypt_init_uios()` dispatches to ZIL, dnode, or normal UIO construction, then appends the MAC vector to the cipher UIO.

## Fault/Test Hooks

- `zfs_key_max_salt_uses` controls salt rotation threshold.
- `zio_decrypt_fail_fraction` can probabilistically force decrypt MAC failures.
- `failed_decrypt_buf` and `failed_decrypt_size` retain failed ciphertext for debugging.

## Key Dependencies

- ICP crypto framework.
- HKDF-SHA512.
- SHA2 and SHA512-HMAC.
- ZFS object type definitions, dnode layout, ZIL layout, block pointer macros, ABD API.
- Called by `zio_encrypt()`/`zio_decrypt()` in `zio.c` and SPA crypto wrappers.

## Notes for Future Readers

- Raw sends drive much of the “portable fields only” authentication design.
- ZIL and dnode blocks are not fully opaque ciphertext; they preserve selected structural metadata in plaintext but authenticate it.
- Indirect block MAC checksums are keyless-verifiable by design.
- Salt rotation reduces IV collision risk for random-IV modes.
