# sources/user-network-fs/samba/source3/smbd/seal.c

## Purpose
This file implements server-side SMB1 transport encryption, historically called sealing. It negotiates a gensec SPNEGO security context with seal support, identifies encrypted packets, decrypts incoming buffers, encrypts outgoing buffers, and tears down partial or active encryption contexts.

## Important APIs, Types, And Functions
The exported API is `is_encrypted_packet`, `srv_free_enc_buffer`, `srv_decrypt_buffer`, `srv_encrypt_buffer`, `srv_request_encryption_setup`, `srv_encryption_start`, and `server_encryption_shutdown`. Internal helpers include `srv_enc_ctx`, `make_auth_gensec`, `make_srv_encryption_context`, and `check_enc_good`. Runtime context is held in global `partial_srv_trans_enc_ctx` during negotiation and `srv_trans_enc_ctx` after successful start; both are `smb_trans_enc_state` objects with gensec state and encryption context numbers.

## Control Flow
Packet detection ignores non-session messages, checks for the `0xFF 'E'` encrypted marker, extracts the encryption context number, and compares it to the active server context. Negotiation starts lazily in `srv_request_encryption_setup`, creating an auth gensec context with `GENSEC_FEATURE_SEAL`, starting SPNEGO as root, then feeding client blobs to `gensec_update`. While more processing is required it returns only a response blob; on success it also returns the two-byte context id in the transaction parameters. `srv_encryption_start` verifies the negotiated context has signing and sealing, frees any old active context, moves the partial context to active, and marks encryption on. Buffer encryption/decryption call common SMB sealing helpers only for session messages and only when an active context exists.

## State And Persistence
State is process-local and talloc-managed: one partial negotiation context and one active transport encryption context. No on-disk state is written. Temporary root privilege is used because gensec may need secrets or keytab access during mechanism start/update. Encrypted outgoing buffers may be newly allocated and must be released through `srv_free_enc_buffer`.

## Dependencies And Integration Points
The file depends on SMB sealing helpers in `libcli/smb/smb_seal.h`, gensec/auth setup, tsocket local/remote addresses, smbd globals, and SMB packet framing helpers. It integrates with SMB1 packet receive/send paths through `proto.h`: receive code can ask whether a packet is encrypted, decrypt buffers before processing, encrypt replies, and shut down contexts when the connection ends.

## Risks And Test Signals
Risks include reliance on global single-context state, accepting only packets whose context number matches the active context, cleanup of partial contexts on negotiation failure, privilege transitions around gensec calls, memory ownership of encrypted buffers, and ensuring signing plus sealing are both negotiated before activation. Tests should cover multi-step SPNEGO setup, failed mechanism start/update, encrypted marker parsing with short or malformed packets, context-number mismatch, encrypt/decrypt round trips, non-session message pass-through, shutdown during partial negotiation, and connection replacement of an existing active context.
