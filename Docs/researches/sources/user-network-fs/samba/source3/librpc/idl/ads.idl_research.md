# sources/user-network-fs/samba/source3/librpc/idl/ads.idl

## Purpose
`ads.idl` defines source3 Active Directory Services connection and wrapping structures for generated headers/NDR stubs. Most structures are `nopull,nopush`, meaning they describe C-side state used by ADS code rather than a normal wire RPC interface.

## Important APIs, types, and functions
- `ads_saslwrap_type` records plain/sign/seal LDAP SASL wrapping modes.
- `ads_auth_flags` encodes bind, SASL, StartTLS/LDAPS, and krb5 config behavior.
- `ads_server`, `ads_auth`, `ads_config`, `ads_saslwrap`, `ads_tlswrap`, and `ads_ldap` describe server discovery, authentication, directory naming context, LDAP buffering, TLS/SASL wrapping, and active LDAP connection state.
- `ads_struct` is the public aggregate used by ADS consumers.

## Control flow
There is no generated wire method flow. The structures model state that ADS LDAP setup, bind, reconnect, SASL wrap, and TLS wrapping code mutates while operating against a domain controller or global catalog.

## State and persistence behavior
The state is in-memory connection state: realm/workgroup/server names, authentication flags and expiry, reconnect pointers, LDAP buffer offsets, socket/TLS descriptors, active address, port, and reconnect timestamps. It does not define durable storage, but fields like `expire_time` and `last_attempt` drive reconnect and credential refresh behavior.

## Dependencies and integration points
The IDL imports NBT and Netlogon flag definitions and conditionally references LDAP/TLS types under `HAVE_ADS`. `libnet_join.idl` accepts an `ads_struct *` in join/unjoin context calls. `ndr_ads.c` supplies empty push/pull hooks because these structs are not meant to be marshalled normally.

## Risks and edge cases
Because many fields are ignored or `nopull,nopush`, generated code will not serialize important pointers. Code must not assume `ads_struct` can be persisted or sent over RPC. Buffer offset/size fields are security-sensitive for LDAP wrapping, and auth flags combine mutually significant transport and SASL decisions.

## Test signals
Build generated headers with and without `HAVE_ADS`; exercise LDAP SASL sign/seal/plain paths, StartTLS/LDAPS flags, reconnect behavior, and join code paths that pass `ads_struct` through libnet join contexts.
