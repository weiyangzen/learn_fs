# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/nsmb_sign_kcf.c

## Purpose

`nsmb_sign_kcf.c` provides kernel-side digest and MAC helpers for SMB1 signing, SMB2 signing, SMB3 signing, one-shot KDF HMAC, and SMB 3.1.1 preauth hashing using KCF.

## Main Interfaces

The file exports MD5 helpers (`nsmb_md5_getmech`, `nsmb_md5_init`, `nsmb_md5_update`, `nsmb_md5_final`), HMAC-SHA256 helpers (`nsmb_hmac_getmech`, `nsmb_hmac_init`, `nsmb_hmac_update`, `nsmb_hmac_final`, `nsmb_hmac_one`), AES-CMAC helpers (`nsmb_cmac_getmech`, `nsmb_cmac_init`, `nsmb_cmac_update`, `nsmb_cmac_final`), and SHA512 helpers (`nsmb_sha512_getmech`, `nsmb_sha512_init`, `nsmb_sha512_update`, `nsmb_sha512_final`).

## Behavior And Data Flow

`find_mech()` maps KCF mechanism names to IDs and logs missing mechanisms. MD5 and SHA512 use `crypto_digest_*` APIs. HMAC-SHA256 and AES-CMAC use `crypto_mac_*` APIs with raw keys measured in bits.

`nsmb_hmac_final()` computes the full SHA-256 HMAC but copies only the first 16 bytes to the caller because SMB2 signatures use a truncated HMAC. `nsmb_cmac_final()` emits the 16-byte AES-CMAC directly. `nsmb_hmac_one()` performs a one-shot MAC and is used by the SMB3 KDF.

Update failures call `crypto_cancel_ctx()` before returning `-1`.

## Dependencies

The file depends on KCF, SMB crypto constants and typedefs from `nsmb_kcrypt.h`, kernel memory/common error headers, and mechanism names such as `SUN_CKM_MD5`, `SUN_CKM_SHA256_HMAC`, `SUN_CKM_AES_CMAC`, and `SUN_CKM_SHA512`.

## Research Notes

This is the low-level signing primitive layer. Higher-level protocol code is responsible for zeroing SMB2 signature fields before MAC calculation and for choosing HMAC vs CMAC. Audit points are context cancellation on error, truncation semantics for SMB2 HMAC, and consistency with the user-space PKCS#11 implementation.
