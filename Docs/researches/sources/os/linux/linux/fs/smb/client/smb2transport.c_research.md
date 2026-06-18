# File Research: sources/os/linux/linux/fs/smb/client/smb2transport.c

## Purpose

`smb2transport.c` implements SMB2/SMB3 transport-adjacent security and request setup logic: signing key lookup, SMB2 HMAC-SHA256 signing, SMB3 AES-CMAC signing, SMB3 key derivation, signature verification, MID allocation, request sequencing, and AEAD crypto transform allocation.

## Main Responsibilities

- Locate session and channel signing keys for SMB2 and SMB3 multichannel.
- Derive SMB3 signing, encryption, and decryption keys for SMB3.0 and SMB3.1.1.
- Sign outgoing SMB2/SMB3 requests when required.
- Verify incoming SMB2/SMB3 response signatures.
- Allocate and initialize MID queue entries, assign message IDs according to credit charge, and add requests to pending MID queues.
- Set up synchronous and asynchronous SMB2 requests before send.
- Allocate AEAD crypto transforms for SMB3 encryption/decryption.

## Key Control Flow

- `smb3_get_sign_key()` finds a session by ID on the primary server, handles channel binding, and selects either the master signing key or per-channel signing key.
- `smb2_get_sign_key()` locates the SMB2 session key from `ses->auth_key.response`.
- `smb2_calc_signature()` signs SMB2 requests using HMAC-SHA256 over the request data.
- `generate_key()` implements the SMB3 KDF-style HMAC derivation using labels, contexts, and 128/256-bit output length selectors.
- `generate_smb30signingkey()` uses SMB3.0 labels/contexts; `generate_smb311signingkey()` uses SMB3.1.1 preauth hash contexts.
- `smb3_calc_signature()` uses AES-CMAC for SMB3 dialects and falls back to SMB2 HMAC for SMB2.1 and earlier.
- `smb2_sign_rqst()` enforces signing only when the request is marked signed, skips signing during negotiate, and uses the dummy early-session signature where required.
- `smb2_verify_signature()` skips commands that are not verified, recalculates the expected signature, and compares with `crypto_memneq()`.
- `smb2_setup_request()` assigns a message ID, allocates and queues a MID, signs the request, and rolls back on failure.
- `smb2_setup_async_request()` performs a similar setup for async requests without session-status filtering.
- `smb3_crypto_aead_allocate()` allocates `gcm(aes)` or `ccm(aes)` transforms depending on negotiated cipher type.

## Dependencies and Integration

- Uses Linux crypto helpers for AEAD, AES-CMAC, SHA-256 HMAC, and constant-time comparison.
- Works with CIFS global session/server lists protected by `cifs_tcp_ses_lock` plus per-session and per-channel locks.
- Integrates with `mid_q_entry`, `pending_mid_q`, credit charge, sequence numbers, and CIFS request send paths.
- Called by send/receive paths declared in `smb2proto.h` and by dialect ops for SMB3 key generation.

## Risk Notes

- Key selection is multichannel-sensitive. Binding a new channel must not overwrite master session keys incorrectly.
- Signing intentionally includes the RFC1002 length prefix only when present as a separate iovec; request layout changes must preserve this behavior.
- Message ID assignment and rollback must stay paired with MID allocation failures to avoid sequence corruption.
- Debug key dumping is gated by `CONFIG_CIFS_DEBUG_DUMP_KEYS` and should remain restricted.
