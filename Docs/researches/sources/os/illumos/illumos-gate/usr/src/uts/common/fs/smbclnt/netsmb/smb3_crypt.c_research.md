# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb3_crypt.c

## Purpose
Implements SMB3 message privacy for the illumos SMB client: crypto mechanism selection, encryption/decryption key derivation after session setup, and in-place SMB3 transform-header encryption/decryption of STREAMS `mblk_t` message chains.

## Key Elements
`nsmb_crypt_init_mech` selects the kernel crypto mechanism for the negotiated cipher, supporting AES-128/256 GCM and AES-128/256 CCM. `nsmb_crypt_fini_mech` clears the stored mechanism state. `nsmb_crypt_init_keys` derives SMB3 client-to-server and server-to-client encryption keys from the session key using SMB KDF labels. SMB 3.1.1 derives keys with preauthentication hash context and supports AES-256 by using the full session key; older SMB3 dialects derive AES-128 CCM keys with the legacy `SMB2AESCCM` labels.

`smb3_msg_encrypt` prepends a 52-byte SMB3 transform header, generates a serialized nonce from per-VC counters protected by `iod_rqlock`, authenticates transform-header fields after the signature, and encrypts the original SMB2 payload in place. It temporarily appends the transform header signature field to the message chain so the crypto helper can write the authentication tag there, then restores the header and links it before the encrypted body.

`smb3_msg_decrypt` splits and validates the transform header, checks the `0xFD SMB` signature, session ID, flags, and body length, trims excess transport padding, configures GCM or CCM authentication parameters from the transform header, temporarily appends the signature/tag region to the ciphertext chain, decrypts in place, then discards the transform header and returns the plaintext body chain.

## Dependencies
Depends on SMB2/SMB3 protocol constants, `smb_vc` negotiated state and session keys, STREAMS message-block helpers, `mbchain`/`mdchain`, illumos random bytes, and `nsmb_kcrypt` AES-GCM/AES-CCM/KDF helpers. The send side assumes the caller holds `vcp->iod_rqlock` as writer so nonce counters are serialized.

## Behavior/Risks
Nonce uniqueness is critical; callers must preserve the locking assumption around `vc3_nonce_low/high`. Encryption is disabled unless the negotiated capabilities include SMB2 encryption and derived keys are present. Transform header parsing is intentionally strict about signature, session ID, flags, and length, so malformed or cross-session encrypted replies fail before decryption. The temporary header/body chain manipulation is sensitive to pointer restoration and error cleanup; leaks or corrupted `b_rptr`/`b_wptr` values would break subsequent transport parsing.
