# File Research: sources/os/linux/linux-stable/fs/smb/server/auth.c

Read status: complete.

## Purpose
Implements ksmbd authentication crypto: NTLMv2 verification, Kerberos handoff, SMB2/3 signing, key derivation, preauth hashing, and SMB3 transform encryption/decryption.

## Main Responsibilities
- Provide static GSS negotiation headers depending on Kerberos support.
- Decode NTLMSSP negotiate/authenticate blobs and verify NTLMv2 challenge responses.
- Build NTLMSSP challenge blobs with target info and server challenge.
- Delegate Kerberos/SPNEGO authentication to userspace IPC when enabled.
- Sign SMB2 with HMAC-SHA256 and SMB3 with AES-CMAC.
- Derive SMB3 signing and encryption/decryption keys for SMB 3.0 and 3.1.1, including channel binding/preauth contexts.
- Compute SMB 3.1.1 preauthentication integrity hashes.
- Encrypt/decrypt SMB3 transform messages using AES-CCM or AES-GCM over scatterlists.

## Dependencies And Role
Depends on user/session state, `crypto_ctx`, transport IPC, NTLMSSP structures, SMB common constants, and Linux crypto primitives. It is called from SMB2 negotiation/session setup and encrypted send/receive paths.

## Risks
High-risk areas include FIPS behavior for NTLMv2, NTLMSSP offset/length validation, session-key exchange decryption, multichannel signing-key selection, AES-256 key length selection, scatterlist construction for vmalloc buffers, and transform-header associated-data handling.
