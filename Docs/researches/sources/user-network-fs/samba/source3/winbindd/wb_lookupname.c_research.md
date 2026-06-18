# sources/user-network-fs/samba/source3/winbindd/wb_lookupname.c

## Purpose
This async helper resolves a domain/name pair to a SID and LSA SID type through the appropriate winbind child domain.

## Important APIs, Types, And Functions
`struct wb_lookupname_state` stores event context, uppercased domain/name, flags, result SID, and result type. Public APIs are `wb_lookupname_send` and `wb_lookupname_recv`.

## Control Flow
The send function uppercases domain and name for cache friendliness, finds a lookup domain from the namespace, and sends `dcerpc_wbint_LookupName` to that child. The callback combines transport and result status and completes. The recv function copies the SID and type to caller-owned outputs.

## State And Persistence
State is request-local. Lookup results may depend on winbind child caches but this file writes no state.

## Dependencies And Integration
It depends on domain lookup by namespace, child handles, generated winbind RPC stubs, SID helpers, and tevent. It is used by higher-level winbind NSS and idmap flows.

## Risks And Test Signals
Test unknown namespace, allocation failures during uppercase copies, names with locale-sensitive characters, RPC status/result failures, and flags propagation. Uppercasing both domain and name can affect case-sensitive backends; cache behavior should be tested with mixed-case input.
