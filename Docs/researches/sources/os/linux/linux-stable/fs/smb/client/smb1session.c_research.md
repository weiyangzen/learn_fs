# File Research: sources/os/linux/linux-stable/fs/smb/client/smb1session.c

This file implements SMB1 session setup authentication. It builds `SMB_COM_SESSION_SETUP_ANDX` requests for NTLMv2, Kerberos/SPNEGO, and RawNTLMSSP, sends them, parses responses, and establishes the session state.

Core structure:
- `struct sess_data` stores xid, session, server, NLS table, current auth state function, result, request length, buffer type, and three iovecs:
  - fixed SMB request,
  - optional SPNEGO/NTLMSSP security blob,
  - strings and remaining BCC area.

Common helpers:
- `cifs_ssetup_hdr()` fills shared session-setup fields, max buffer/mpx counts, VC number, session key id, flags2, and capability bits.
- Unicode and ASCII helpers encode user, domain, OS, and LAN manager strings.
- Response decoders parse returned server OS, NOS, and domain strings.
- `sess_alloc_buffer()` allocates the fixed SMB buffer and a 2000-byte string buffer.
- `sess_free_buffer()` zeroes/free sensitive buffers.
- `sess_sendreceive()` computes BCC, sends three-vector requests through `SendReceive2()`, and replaces request buffer with the response.
- `sess_establish_session()` copies the auth key into the server session key when signing is enabled, initializes SMB1 sequence numbering, and marks `server->session_estab`.

Authentication flows:
- `sess_auth_ntlmv2()` sends old-style no-extended-security NTLMv2 session setup, embeds the NTLMv2 response after the fixed request, validates response word count 3, stores `Suid`, decodes strings, and establishes the session.
- `sess_auth_kerberos()` is built under `CONFIG_CIFS_UPCALL`; it gets a SPNEGO key from userspace upcall, validates version, stores the session key, sends an extended-security blob, validates response word count 4 and blob length, decodes strings, and establishes the session.
- RawNTLMSSP is a two-step state machine: `sess_auth_rawntlmssp_negotiate()` sends negotiate, accepts `NT_STATUS_MORE_PROCESSING_REQUIRED`, decodes the NTLMSSP challenge, and schedules `sess_auth_rawntlmssp_authenticate()`; authenticate sends the auth blob with the challenge UID, validates response, decodes returned strings, establishes the session, and cleans sensitive state.

Dispatch:
- `select_sec()` calls `cifs_select_sectype()` and chooses NTLMv2, Kerberos, or RawNTLMSSP. Unsupported or unavailable methods return errors.
- `CIFS_SessSetup()` allocates `sess_data`, selects security, runs state functions until completion, and returns the stored result.

Risk points:
- Security blob lengths and word counts are explicitly validated.
- Sensitive auth material is freed with `kfree_sensitive()` or zeroed before release.
- Kerberos requires `CONFIG_CIFS_UPCALL`; otherwise selection fails with `-ENOSYS`.
