# File Research: sources/os/linux/linux/fs/smb/server/asn1.c

This file wraps Linux ASN.1 BER decoding for SPNEGO negotiation and builds SPNEGO NTLMSSP response blobs.

Main behavior:
- `ksmbd_decode_negTokenInit()` and `ksmbd_decode_negTokenTarg()` call generated ASN.1 decoders with `struct ksmbd_conn` as context.
- `encode_asn_tag()` and `compute_asn_hdr_len_bytes()` encode short/long BER lengths for generated response blobs.
- `build_spnego_ntlmssp_neg_blob()` builds a negTokenTarg response containing negotiation result, NTLMSSP OID, and an NTLM blob.
- `build_spnego_ntlmssp_auth_blob()` builds a final auth response with success/failure negotiation result.
- ASN.1 callbacks validate SPNEGO OIDs, record supported auth mechanisms on the connection, select the first preferred mechanism, and copy mech tokens with `kmemdup_nul()`.

It depends on generated headers `ksmbd_spnego_negtokeninit.asn1.h` and `ksmbd_spnego_negtokentarg.asn1.h`, Linux OID lookup, and auth-mechanism constants from `auth.h`.
