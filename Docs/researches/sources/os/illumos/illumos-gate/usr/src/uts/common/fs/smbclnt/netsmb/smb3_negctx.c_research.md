# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb3_negctx.c

## Purpose
Encodes and decodes SMB 3.1.1 negotiate contexts for preauthentication integrity and encryption cipher negotiation.

## Key Elements
`smb3_negctxs_encode` aligns the negotiate-context section to 8 bytes and emits two contexts: required `SMB2_PREAUTH_INTEGRITY_CAPABILITIES` with SHA-512 and a random 32-byte salt, and `SMB2_ENCRYPTION_CAPABILITIES` listing enabled ciphers in preference order. The tunable `nsmb_ciphers_enabled` bitmask allows testing with selected ciphers disabled; by default it advertises all four supported AES ciphers, preferring AES-256 and GCM over CCM.

`smb3_negctxs_decode` parses the server's SMB 3.1.1 negotiate-context response, enforcing count bounds, 8-byte context alignment, per-context length sanity, exactly one preauth context, exactly one SHA-512 hash selection, and at most one encryption context. It skips unknown context types and context padding but rejects duplicate required/recognized contexts and invalid lengths. The selected preauth hash ID and encryption cipher are stored in the VC as `vc3_preauth_hashid` and `vc3_enc_cipherid`.

## Dependencies
Uses `mbchain` and `mdchain` binary encoders/decoders, SMB2/SMB3 protocol constants, random salt generation, DTrace probes, SHA-512 definitions from `nsmb_kcrypt`, and negotiated VC state in `smb_conn.h`.

## Behavior/Risks
This is a negotiation trust boundary. Bad alignment, excessive context lengths, missing or duplicate preauth contexts, unsupported preauth hash IDs, and invalid encryption cipher counts abort negotiation. Lack of an encryption context or no acceptable cipher is not fatal by itself; the VC records `SMB3_CIPHER_NONE`, and later tree connect or encrypted-message requirements determine whether the session can continue. Edits must preserve padding/offset accounting because the SMB2 negotiate-context list is 8-byte aligned and may include unknown future contexts.
