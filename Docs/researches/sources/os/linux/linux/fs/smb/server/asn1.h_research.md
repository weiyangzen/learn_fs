# File Research: sources/os/linux/linux/fs/smb/server/asn1.h

This header declares the SPNEGO ASN.1 entry points used by KSMBD session setup.

Exports:
- `ksmbd_decode_negTokenInit()`
- `ksmbd_decode_negTokenTarg()`
- `build_spnego_ntlmssp_neg_blob()`
- `build_spnego_ntlmssp_auth_blob()`

The decode APIs take a security blob and `struct ksmbd_conn`; the build APIs allocate output blobs and return their lengths.
