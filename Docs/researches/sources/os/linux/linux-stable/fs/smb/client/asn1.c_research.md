# File Research: sources/os/linux/linux-stable/fs/smb/client/asn1.c

## Purpose

Implements CIFS SPNEGO NegTokenInit ASN.1 decoder callbacks that detect server-supported authentication mechanisms from a security blob.

## Main Responsibilities

- `decode_negTokenInit()` runs the generated `cifs_spnego_negtokeninit_decoder` over a server security blob and returns boolean success.
- `cifs_gssapi_this_mech()` validates that the top-level GSSAPI mechanism OID is SPNEGO and rejects unexpected OIDs with `-EBADMSG`.
- `cifs_neg_token_init_mech_type()` parses mechanism OIDs from NegTokenInit and sets capability booleans on `struct TCP_Server_Info`:
  - `sec_mskerberos`
  - `sec_kerberosu2u`
  - `sec_kerberos`
  - `sec_ntlmssp`
  - `sec_iakerb`
- Logs unsupported or unexpected OIDs using CIFS debug logging and OID string formatting.

## Integration Notes

- Depends on generated header `cifs_spnego_negtokeninit.asn1.h`.
- Uses kernel OID registry helpers `look_up_OID()` and `sprint_oid()`.
- The decoded server security capability flags feed later session setup and upcall selection.
