# File Research: sources/os/linux/linux/fs/smb/client/asn1.c

ASN.1 decoder callbacks for CIFS SPNEGO negotiation-token parsing.

`decode_negTokenInit()` invokes the generated `cifs_spnego_negtokeninit_decoder` against a server context and returns boolean success. `cifs_gssapi_this_mech()` validates that the outer GSSAPI mechanism OID is SPNEGO, logging and returning `-EBADMSG` on unexpected OIDs.

`cifs_neg_token_init_mech_type()` records advertised mechanism support into `TCP_Server_Info` flags for Microsoft Kerberos, Kerberos user-to-user, Kerberos, NTLMSSP, and IAKERB. Unsupported OIDs are logged at FYI level but are not fatal.
