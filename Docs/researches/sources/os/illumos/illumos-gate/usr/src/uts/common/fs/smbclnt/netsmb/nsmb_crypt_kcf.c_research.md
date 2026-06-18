# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/nsmb_crypt_kcf.c

## Purpose

`nsmb_crypt_kcf.c` provides kernel-side SMB3 encryption and decryption helpers backed by the Kernel Cryptographic Framework. It intentionally keeps SMB-specific knowledge limited to constants and structures from `nsmb_kcrypt.h`.

## Main Interfaces

The file exports `nsmb_aes_ccm_getmech()`, `nsmb_aes_gcm_getmech()`, `nsmb_crypto_init_ccm_param()`, `nsmb_crypto_init_gcm_param()`, `nsmb_encrypt_init()`, `nsmb_decrypt_init()`, `nsmb_enc_ctx_done()`, `nsmb_encrypt_mblks()`, and `nsmb_decrypt_mblks()`.

## Behavior And Data Flow

`find_mech()` maps mechanism names such as `SUN_CKM_AES_CCM` and `SUN_CKM_AES_GCM` to KCF mechanism IDs. The CCM and GCM parameter initializers populate KCF parameter structures with nonce, authenticated data, tag/MAC size, and data size where required.

`nsmb_encrypt_init()` and `nsmb_decrypt_init()` stash a raw key in `crypto_key_t`, with key length converted to bits. There is no KCF context setup until whole-message encrypt/decrypt calls.

`nsmb_encrypt_mblks()` encrypts an mblk chain in place using `crypto_encrypt()`. It treats input length as cleartext length and output length as cleartext plus the 16-byte SMB2 signature/tag size. `nsmb_decrypt_mblks()` rejects ciphertext shorter than or equal to the tag size and decrypts in place, producing ciphertext length minus tag size.

## Dependencies

The file depends on KCF APIs, STREAMS mblk crypto data support, `msgsize()`, SMB crypto constants in `nsmb_kcrypt.h`, and mechanism names from illumos crypto headers.

## Research Notes

The primary correctness constraints are mblk length accounting, tag-size assumptions, nonce-size assertions, and matching KCF CCM/GCM parameters to SMB3 transform-header construction elsewhere. Failures log KCF return codes and return `-1`.
