# sources/user-network-fs/cifs-utils/spnego.h

## Purpose
`spnego.h` declares SPNEGO/Kerberos OID constants, GSS token identifiers, and the encoder functions implemented by `spnego.c`.

## Important APIs and types
The header defines `OID_SPNEGO`, `OID_NTLMSSP`, `OID_KERBEROS5_OLD`, and `OID_KERBEROS5`. It also defines token-id byte strings for Kerberos AP-REQ/AP-REP/error and GSS MIC/wrap. It declares `gen_negTokenInit(const char *OID, DATA_BLOB blob)` and `spnego_gen_krb5_wrap(const DATA_BLOB ticket, const uint8_t tok_id[2])`.

## Control flow and state
The header has no runtime control flow or persistence. It is a compile-time contract for authentication token construction.

## Dependencies and integration points
It assumes `DATA_BLOB` and `uint8_t` are visible to includers before or through local include ordering. It is consumed by SPNEGO encoders and authentication helpers in cifs-utils.

## Risks
The token-id macros cast string literals to mutable `unsigned char *`, which can trigger const-correctness warnings and unsafe mutation if callers write through them. The header itself does not include `stdint.h` or `data_blob.h`, so standalone inclusion can fail depending on include order.

## Test signals
Compile tests should include this header directly in isolation and with strict warnings. API tests should verify token-id values and OID strings against expected SPNEGO/Kerberos constants.
