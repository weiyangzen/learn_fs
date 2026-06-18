# File Research: sources/os/linux/linux/fs/smb/client/smb1encrypt.c

This file implements SMB1 signing and signature verification using MD5 over the session key and SMB request data.

Key functions:
- `cifs_calc_signature()` initializes MD5, hashes the server session key, and delegates request-vector hashing to `__cifs_calc_signature()`. It rejects missing inputs and returns `-EOPNOTSUPP` when FIPS mode disables MD5.
- `cifs_sign_rqst()` writes the SMB1 sequence number into the signature field, advances the server sequence counter, computes the signature, and copies the first 8 bytes into the SMB header. Before a session is established it writes the SMB1 dummy signature string.
- `cifs_verify_signature()` skips verification before session establishment and for oplock-release locking requests, preserves the server signature, recomputes the expected signature using the response sequence number, and compares with `crypto_memneq()`.

Important invariants:
- Signing is conditional on the SMB header security-signature flag and not performed while the server needs negotiate.
- The signing path expects the server mutex to be held where noted.
- Sequence-number handling is central: requests consume paired request/response sequence values.

Security relevance:
- SMB1 signing relies on MD5, so this path is incompatible with FIPS mode and is legacy/security-sensitive by design.
