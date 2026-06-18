# sources/user-network-fs/samba/source3/include/auth_generic.h

## Purpose
`auth_generic.h` declares client-side generic authentication helpers wrapping credentials and GENSEC security negotiation.

## Important APIs, Types, And Functions
- `struct auth_generic_state` owns client credentials and a `gensec_security` context.
- Setters update username, domain, password, or whole credential object.
- `auth_generic_client_prepare()` allocates/prepares state.
- Start functions begin authentication by OID, mechanism name, DCE/RPC auth type/level, or SASL mechanism list.

## Control Flow
Callers prepare a state, set credentials, choose a start method matching the protocol, and then continue negotiation through the underlying GENSEC context.

## State And Persistence
State is in talloc-owned credentials and GENSEC objects. No disk persistence is defined.

## Dependencies And Integration Points
It integrates source3 clients with Samba credential objects, GENSEC, SASL selection, and DCE/RPC authentication type negotiation.

## Risks
Credential ownership and lifetime must be clear when passing a `cli_credentials` pointer. Starting by SASL list depends on mechanism ordering and server capabilities. Password setters handle sensitive data and must avoid logging/copy leaks in implementations.

## Test Signals
Test username/domain/password setters, external credential injection, NTLM/Kerberos/SPNEGO/SASL mechanism selection, invalid OIDs/names, and memory cleanup.
