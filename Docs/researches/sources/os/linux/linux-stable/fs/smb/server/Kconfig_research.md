# File Research: sources/os/linux/linux-stable/fs/smb/server/Kconfig

Read status: complete.

## Purpose
Declares kernel configuration options for the ksmbd SMB3 server.

## Main Contents
- `SMB_SERVER` tristate with dependencies on networking, multiuser, and file locking.
- Crypto, ASN.1, NLS, OID registry, and CRC32 selections required by SMB3 auth/signing/encryption.
- `SMB_SERVER_SMBDIRECT` for optional RDMA/SMB Direct support.
- `SMB_SERVER_CHECK_CAP_NET_ADMIN` and `SMB_SERVER_KERBEROS5` toggles.

## Dependencies And Role
Controls whether ksmbd is built and which transport/authentication features are compiled.

## Risks
Config selections must match code assumptions. Missing crypto/ASN.1 selections would break negotiated SMB3 security features; SMB Direct has strict InfiniBand dependency constraints.
