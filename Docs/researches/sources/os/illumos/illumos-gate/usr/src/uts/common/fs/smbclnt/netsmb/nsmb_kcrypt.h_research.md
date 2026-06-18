# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/nsmb_kcrypt.h

## Purpose

`nsmb_kcrypt.h` defines the shared SMB client crypto abstraction used by signing, preauth hashing, key derivation, and encryption code. It supports both kernel KCF and user-space PKCS#11 implementations via conditional typedefs.

## Main Interfaces

The header defines key and digest constants such as `AES128_KEY_LENGTH`, `AES256_KEY_LENGTH`, `MD5_DIGEST_LENGTH`, `SHA256_DIGEST_LENGTH`, `SHA512_DIGEST_LENGTH`, `SMB2_SIG_SIZE`, `SMB2_KEYLEN`, `SMB3_AES_CCM_NONCE_SIZE`, and `SMB3_AES_GCM_NONCE_SIZE`.

Kernel builds map `smb_crypto_mech_t` to `crypto_mechanism_t` and `smb_sign_ctx_t` to `crypto_context_t`; user builds map them to PKCS#11 types. `smb_enc_ctx_t` wraps mechanism parameters, key material or key handles, and encryption context state.

Function prototypes cover MD5, HMAC-SHA256, AES-CMAC, SHA512, one-shot HMAC, SMB3 KDF, AES-CCM/GCM parameter initialization, encrypt/decrypt initialization, mblk encrypt/decrypt, and context cleanup.

## Dependencies

Kernel compilation depends on `<sys/crypto/api.h>`; user-space compilation depends on PKCS#11 headers. Both variants include STREAMS and UIO types because the crypto helpers operate on SMB message buffers.

## Research Notes

This header is the contract between higher-level SMB2/3 protocol code and the concrete kernel/user crypto implementations. Compatibility risks come from keeping structure layouts and function semantics aligned with the parallel user-space implementation and with SMB server-side crypto abstractions.
