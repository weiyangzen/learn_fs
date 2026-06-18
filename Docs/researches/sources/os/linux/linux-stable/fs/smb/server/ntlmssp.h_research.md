# File Research: sources/os/linux/linux-stable/fs/smb/server/ntlmssp.h

This header defines NTLMSSP constants, flags, wire-format message structures, AV pair identifiers, and per-session NTLMSSP authentication state used by ksmbd authentication code.

Constants:
- `NTLMSSP_SIGNATURE`: `"NTLMSSP"`.
- `TGT_Name`: `"KSMBD"`.
- Key and ciphertext sizes:
  - `CIFS_CRYPTO_KEY_SIZE`: 8
  - `CIFS_KEY_SIZE`: 40
  - `CIFS_ENCPWD_SIZE`: 16
  - `CIFS_CPHTXT_SIZE`: 16
- Message types:
  - `NtLmNegotiate`
  - `NtLmChallenge`
  - `NtLmAuthenticate`
  - `UnknownMessage`

Negotiate flags:
- Defines NTLMSSP flags for Unicode/OEM strings, target request/type, signing/sealing, LM/NTLM choices, anonymous auth, domain/workstation supplied, always-sign, extended security, target info, version, 128-bit, key exchange, and 56-bit support.

Enums:
- `enum av_field_type`
  - AV pair IDs from `NTLMSSP_AV_EOL` through `NTLMSSP_AV_CHANNEL_BINDINGS`.

Wire structures:
- `struct security_buffer`
  - Length, maximum length, and buffer offset.
- `struct target_info`
  - Type, length, and variable content.
- `struct negotiate_message`
  - Type 1 client negotiate message.
- `struct challenge_message`
  - Type 2 server challenge message.
- `struct authenticate_message`
  - Type 3 client authenticate message.
- `struct ntlmv2_resp`
  - NTLMv2 response blob prefix.

Session state:
- `struct ntlmssp_auth`
  - Whether session key is per SMB session.
  - Client and connection flags.
  - Challenge ciphertext.
  - NTLMSSP crypto key.

Role:
- Protocol wire-format header for authentication exchange; included by session management and auth implementation.

Risk areas:
- All wire structures are `__packed`; code must use little-endian helpers and avoid assuming natural alignment.
- Security buffer offsets and lengths are client-controlled in incoming messages and require strict validation in parser code.
- `sizeof(NTLMSSP_SIGNATURE)` includes the trailing NUL, matching the structures here; parser code must be consistent with that convention.
