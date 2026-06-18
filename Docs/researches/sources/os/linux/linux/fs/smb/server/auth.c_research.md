# File Research: sources/os/linux/linux/fs/smb/server/auth.c

This file implements KSMBD authentication, signing, key derivation, preauth hashing, and SMB3 encryption/decryption.

Main areas:
- SPNEGO negotiate header: `ksmbd_copy_gss_neg_header()` copies a fixed GSS/SPNEGO header, with Kerberos OIDs included when `CONFIG_SMB_SERVER_KERBEROS5` is enabled.
- NTLMv2: computes the NTLMv2 hash from passkey, uppercase UTF-16 username, and domain; verifies the client response; derives the session key; handles optional key exchange via ARC4.
- NTLMSSP parsing/building: validates negotiate/authenticate blobs, stores client flags, generates challenge blobs with target info and random challenge.
- Kerberos: when enabled, delegates SPNEGO authentication to userspace IPC and builds/validates the session user plus session key; otherwise returns `-EOPNOTSUPP`.
- Signing: SMB2 uses HMAC-SHA256; SMB3 uses AES-CMAC.
- SMB3 keys: derives SMB 3.0 and SMB 3.1.1 signing/encryption/decryption keys using dialect-specific labels and contexts, including preauth hash context for 3.1.1.
- Encryption: `ksmbd_crypt_message()` uses AES-GCM or AES-CCM AEAD with scatterlists spanning response/request iovecs and transform-header associated data.

Security-sensitive dependencies include Linux crypto, FIPS gating for NTLMv2, session/user state, preauth session lookup, and the pooled AEAD context manager in `crypto_ctx.c`.
