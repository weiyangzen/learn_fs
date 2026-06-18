# File Research: sources/os/linux/linux/fs/smb/server/ntlmssp.h

This header defines NTLMSSP constants and packed wire structures used by ksmbd authentication.

Protocol constants:
- Signature: `NTLMSSP_SIGNATURE`.
- Target name: `TGT_Name` as `KSMBD`.
- Key and ciphertext sizes: `CIFS_CRYPTO_KEY_SIZE`, `CIFS_KEY_SIZE`, `CIFS_ENCPWD_SIZE`, and `CIFS_CPHTXT_SIZE`.
- Message type constants for negotiate, challenge, authenticate, and unknown messages.
- Full NTLMSSP negotiate flag set for Unicode/OEM strings, signing, sealing, NTLM, domain/workstation supplied, target info, version, 128-bit, key exchange, and 56-bit negotiation.

Wire structures:
- `struct security_buffer` models NTLMSSP length/max-length/offset triples.
- `struct target_info` models AV-pair records.
- `struct negotiate_message`, `challenge_message`, and `authenticate_message` are packed layouts for the three NTLMSSP exchange messages.
- `struct ntlmv2_resp` models the NTLMv2 response prefix.
- `struct ntlmssp_auth` stores per-session NTLMSSP negotiation state, connection/client flags, ciphertext, and challenge key.

Role in this group:
- Included by `user_session.h` for `CIFS_KEY_SIZE` session-key storage.
- Used by ksmbd authentication code outside this group to parse and produce NTLMSSP security blobs during SMB2 session setup.

Security relevance:
- Structures are `__packed` and endian-annotated for direct wire parsing.
- The header contains layout definitions only; validation and cryptographic operations happen in auth code.
