# File Research: sources/os/linux/linux-stable/fs/smb/client/smb2transport.c

## Summary
Implements SMB2/SMB3 transport-layer signing, signature verification, key derivation, MID allocation/setup, session/tcon lookup by SMB identifiers, receive checking, and AEAD crypto allocation. It is the cryptographic and request-tracking support layer under the SMB2 PDU workers.

## Main Responsibilities
- Find session signing keys for SMB2 and per-channel SMB3 signing keys for multichannel connections.
- Look up non-exiting sessions and tree connections by SessionId and TreeId from incoming SMB2 headers.
- Compute SMB2 HMAC-SHA256 signatures and SMB3 AES-CMAC signatures over request vectors.
- Generate SMB3 signing, encryption, and decryption keys using dialect-specific labels and contexts.
- Support SMB3.0 key derivation and SMB3.1.1 preauth-hash-based key derivation, including AES-256 full-session-key handling.
- Sign outgoing requests when `SMB2_FLAGS_SIGNED` is set and session state permits signing.
- Verify incoming signed responses unless the command or connection state exempts verification.
- Allocate and initialize MID queue entries, assign message ids, charge multi-credit requests, and insert synchronous requests into pending MID queues.
- Set up synchronous and asynchronous requests with message ids and signatures.
- Check received responses by verifying signatures and mapping SMB status codes to Linux errors.
- Allocate kernel AEAD transforms for SMB3 encryption/decryption based on negotiated cipher type.

## Key Interfaces
- Lookup helpers: `smb2_find_smb_tcon()` and internal session/tcon lookup routines.
- Signing and verification: `smb2_verify_signature()`, internal `smb2_calc_signature()`, `smb3_calc_signature()`, and `smb2_sign_rqst()`.
- Key derivation: `generate_smb30signingkey()` and `generate_smb311signingkey()`.
- Request setup: `smb2_setup_request()` and `smb2_setup_async_request()`.
- Receive/error handling: `smb2_check_receive()`.
- Crypto allocation: `smb3_crypto_aead_allocate()`.

## Control Flow And Behavior
Signing key lookup differs by dialect. SMB2 uses the session `auth_key.response`; SMB3 uses the session or channel signing key, and binding a new channel uses the master session key until that channel key is established. Key derivation writes a primary session signing key, per-channel signing key, and encryption/decryption keys for established sessions; channel binding only updates the new channel signing key.

Outgoing setup assigns a message id, creates a MID, queues it when synchronous, and signs the request. If MID allocation or signing fails, the message id is reverted and the MID is deleted or released. Signature calculation strips an RFC1002 length vector when present by hashing it first and then signing the remaining SMB request data in the form expected by shared CIFS signing helpers.

Incoming verification saves the server signature, zeroes the header signature, recomputes it using the negotiated key and dialect algorithm, and compares with `crypto_memneq()`. Negotiate, session setup, oplock break, ignored-signature connections, and pre-session-established responses are skipped.

## State And Synchronization
Session and channel lookup is protected with `cifs_tcp_ses_lock`, `ses_lock`, and `chan_lock`; MID insertion uses `mid_queue_lock`; key derivation touches session/channel key slots under the session/channel locks where required. Request setup assumes the caller holds the appropriate server mutex according to CIFS send-path conventions.

## Cross-File Interactions
`smb2pdu.c` calls this file for signing-key generation after session setup, response signature verification in async I/O, AEAD allocation after negotiation, and MID setup indirectly through the send path. `connect.c` and demultiplex code use `smb2_find_smb_tcon()` to route unsolicited and response-related events such as oplock/lease breaks.

## Risks
Multichannel key selection and binding state are subtle: using the wrong key breaks signing or weakens channel isolation. Message-id rollback must stay aligned with credit charge. Signature calculation must include exactly the same byte stream that the server signs, including RFC1002 handling and encrypted/decrypted response state. AEAD allocation failure handling must avoid leaving one transform allocated without the other.
