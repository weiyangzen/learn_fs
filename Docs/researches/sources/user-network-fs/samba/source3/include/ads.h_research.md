# sources/user-network-fs/samba/source3/include/ads.h

## Purpose
`ads.h` is the source3 Active Directory Services wrapper header. It centralizes LDAP/Kerberos ADS types, reconnect state, SASL wrap operations, LDAP control OIDs, and generated ADS prototypes.

## Important APIs, Types, And Functions
- `struct ads_saslwrap_ops` defines SASL wrap/unwrap/disconnect callbacks.
- `struct ads_reconnect_state` stores a credential-producing callback and private data for reconnect handling.
- `ADS_STRUCT` aliases `struct ads_struct`.
- `ADS_MODLIST` is `LDAPMod **` when ADS/LDAP support is compiled in, otherwise `void **`.
- LDAP control OIDs cover paging, no referrals, server sort, permissive modify, ASQ, extended DN, and SD flags.
- `ads_extended_dn_flags` and `ads_control` describe control values passed into LDAP operations.
- Includes generated `ads_proto.h`, LDAP prototypes when available, and Kerberos prototypes.

## Control Flow
The header has no executable flow, but ADS callers include it to access generated functions and to choose compile-time LDAP-capable or stub-compatible types.

## State And Persistence
No state is stored here. The declared types support LDAP connections, reconnect credential callbacks, and SASL wrapping state owned by implementation modules.

## Dependencies And Integration Points
It integrates source3 with libads, LDAP, Kerberos, generated NDR ADS definitions, and Samba credential handling. Conditional typedefs keep non-ADS builds compiling.

## Risks
Conditional `ADS_MODLIST` typing can hide code paths that compile without LDAP but fail at runtime if not guarded. OID string constants are protocol contracts. Reconnect callbacks must manage talloc ownership of returned credentials correctly.

## Test Signals
Build with and without `HAVE_ADS`/`HAVE_LDAP`, test LDAP controls in ADS searches/modifies, SASL wrap/unwrap flows, reconnect callback behavior, and ownership cleanup through `ADS_TALLOC_CONST_FREE`.
