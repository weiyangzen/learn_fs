# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/auth.c

CIFS/SMB authentication response and packet-signature support.

Key behavior:
- Supports `plain`, `lm+ntlm`, `ntlm`, and `ntlmv2` authentication methods; default is `ntlmv2`.
- `auth_plain` obtains a plaintext password via Plan 9 auth and stores it for plaintext SMB session setup.
- `auth_proto` calls `auth_respond` for NTLM/NTLMv2 challenge response and extracts LM/NT response buffers.
- `auth_ntlm` suppresses weak LM response by copying the NT response into both response slots.
- `getauth` selects the method, rejects implicit plaintext auth unless explicitly requested, and reports supported methods on error.
- `genmac` computes SMB signing MD5 over the MAC key and packet, after temporarily replacing signature bytes with the sequence number.
- `macsign` signs outgoing packets or verifies incoming signatures, using the placeholder `BSRSPYL ` before sequence generation starts.

Dependencies:
- Includes Plan 9 auth, libsec MD5, 9P/thread headers, and `cifs.h`.
- Uses `Session`, `Auth`, and `Pkt` fields defined in CIFS headers.

Research notes:
- Comments explicitly warn LM/NTLM weaknesses and recommend Kerberos for real security, though Kerberos is not implemented here.
