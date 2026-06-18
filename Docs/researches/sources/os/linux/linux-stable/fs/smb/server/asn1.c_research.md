# File Research: sources/os/linux/linux-stable/fs/smb/server/asn1.c

Read status: complete.

## Purpose
Implements SPNEGO ASN.1/BER decode callbacks and NTLMSSP SPNEGO response blob builders for ksmbd authentication.

## Main Responsibilities
- Decode `negTokenInit` and `negTokenTarg` blobs with generated ASN.1 decoders.
- Build SPNEGO-wrapped NTLMSSP challenge and final auth response blobs.
- Validate GSS mechanism OIDs and record supported/preferred auth mechanisms on the connection.
- Copy mechanism tokens from decoded SPNEGO messages into `conn->mechToken`.

## Key Interfaces
`ksmbd_decode_negTokenInit()`, `ksmbd_decode_negTokenTarg()`, `build_spnego_ntlmssp_neg_blob()`, `build_spnego_ntlmssp_auth_blob()`, and generated-decoder callbacks such as `ksmbd_neg_token_init_mech_type()`.

## Risks
ASN.1 length encoding and token copying are security-sensitive. Incorrect bounds, OID handling, or allocated token lifetime can break session setup or expose malformed-client parsing bugs.
