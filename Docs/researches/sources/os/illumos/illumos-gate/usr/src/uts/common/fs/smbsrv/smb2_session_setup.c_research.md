# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_session_setup.c

Implements SMB2 session setup dispatch.

Key behavior:
- Decodes session setup request fields and security blob.
- Rejects required-encryption configurations when the negotiated dialect/client capabilities cannot support encryption.
- Rejects SMB3 session binding/multi-channel because it is unsupported.
- Delegates authentication to `smb_authenticate_ext()`.
- On success, sets guest/null/encrypt-data session flags and raises session credits.
- Logs off a previous session ID when supplied by the client and different from the current session.
- Encodes response security blob for success or more-processing-required.

Important dependencies:
- Authentication: `smb_authenticate_ext`.
- Credit management: `smb2_ss_adjust_credits`.
- Server/user encryption policy fields.

Notable details:
- Session setup request capabilities are intentionally ignored because negotiate capabilities are authoritative.
