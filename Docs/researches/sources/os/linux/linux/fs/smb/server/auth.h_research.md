# File Research: sources/os/linux/linux/fs/smb/server/auth.h

This header declares authentication and cryptographic APIs for KSMBD.

Key definitions:
- GSS header length/padding differ depending on Kerberos support.
- NTLM/SMB hash and signature sizes.
- Auth mechanism bit flags for NTLMSSP, Kerberos, MS Kerberos, and Kerberos user-to-user.

Exported APIs cover:
- SMB3 message encryption/decryption.
- GSS negotiate header copy.
- NTLMv2 authentication and NTLMSSP blob parsing/challenge generation.
- Kerberos authentication.
- SMB2/SMB3 signing.
- SMB 3.0/3.1.1 signing and encryption key derivation.
- SMB 3.1.1 preauth integrity hash generation.
