# File Research: sources/os/linux/linux-stable/fs/smb/server/auth.h

Read status: complete.

## Purpose
Declares ksmbd authentication, signing, encryption, and key-derivation interfaces.

## Main Contents
- GSS header length/padding constants conditional on Kerberos support.
- NTLM/CIFS hash and session-key sizes.
- Auth mechanism bit flags for NTLMSSP and Kerberos variants.
- Prototypes for NTLMSSP parsing, challenge building, Kerberos auth, signing, key derivation, preauth hashing, and message encryption/decryption.

## Dependencies And Role
Included by authentication/session setup and SMB2 crypto paths.

## Risks
Function signatures encode buffer ownership and key-size assumptions. Any mismatch with `auth.c` or SMB2 session setup can break signing/encryption interoperability.
