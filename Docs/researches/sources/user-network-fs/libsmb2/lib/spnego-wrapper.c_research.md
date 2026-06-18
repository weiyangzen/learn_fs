<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/spnego-wrapper.c -->
# sources/user-network-fs/libsmb2/lib/spnego-wrapper.c

Purpose: Implements libsmb2's SPNEGO/GSS-API ASN.1 BER token wrapping and unwrapping for SMB authentication, including NTLMSSP and optional Kerberos mechanism negotiation.

Important APIs, types, and functions: Defines static OIDs for GSS-SPNEGO, Kerberos, Microsoft Kerberos, and NTLMSSP; `oid_compare`; wrapper creators `smb2_spnego_create_negotiate_reply_blob`, `smb2_spnego_wrap_gssapi`, `smb2_spnego_wrap_ntlmssp_challenge`, `smb2_spnego_wrap_ntlmssp_auth`, and `smb2_spnego_wrap_authenticate_result`; and parsers `smb2_spnego_unwrap_targ`, `smb2_spnego_unwrap_gssapi`, and `smb2_spnego_unwrap_blob`.

Control flow: The wrapping functions allocate a BER output buffer, emit nested application/context/sequence nodes, reserve length fields, copy mechanism tokens where needed, then patch lengths. The unwrap path peeks at the first byte, recognizes raw NTLMSSP, application GSS blobs, or context-tagged SPNEGO target tokens, then decodes OIDs, mechanism flags, negotiation result, and response token pointers.

State and persistence behavior: No persistent state is stored. Returned blobs are heap allocated for the caller to free. Unwrapped tokens are pointers into the caller-supplied input buffer. Errors are stored on `struct smb2_context` unless suppressed.

Dependencies and integration points: Depends on libsmb2 private context/error handling and `asn1-ber` helpers. It is used by SMB session setup authentication paths and must agree with NTLMSSP/Kerberos code about mechanism flags from `spnego-wrapper.h`.

Risks: The buffer sizing is heuristic (`256 + 4 * token_len`, `64 + 2 * token_len`) and relies on ASN.1 helpers respecting `dst_size`. Parser macros use minimum lengths that can reject unusual but valid encodings. `smb2_spnego_unwrap_targ` accepts `mechanisms` without a NULL guard in the negResult branch. A typo in error text says `spengo`.

Test signals: Indirectly exercised by authentication tests and `ntlmssp_generate_blob.c`; no dedicated SPNEGO malformed-input unit test is present in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/spnego-wrapper.c -->
