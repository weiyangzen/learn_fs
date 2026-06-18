# sources/user-network-fs/samba/source4/libnet/libnet_lookup.c

## Purpose
`libnet_lookup.c` implements libnet name and DC lookup helpers. It resolves NetBIOS hostnames to addresses, finds writable LDAP/DS DCs via CLDAP, and resolves account/group names to SIDs through LSA.

## Important APIs, Types, And Functions
Public APIs are `libnet_Lookup_send/recv()` and `libnet_Lookup()`, `libnet_LookupHost_send()` and `libnet_LookupHost()`, `libnet_LookupDCs_send/recv()` and `libnet_LookupDCs()`, and `libnet_LookupName_send/recv()` and `libnet_LookupName()`.

`lookup_state` carries the `nbt_name` and resolved address. `lookup_name_state` carries the LSA domain-open prerequisite, one-name `lsa_LookupNames` request, returned SID array/domain list, and monitor callback. `prepare_lookup_params()` initializes the single-name LSA lookup structures.

## Control Flow
`libnet_Lookup_send()` validates hostname input, builds an NBT name using the requested type, chooses either caller-provided `resolve_ctx` or `ctx->resolve_ctx`, and calls `resolve_name_send()`. Receive wraps the single resolved address in a one-element string list.

`libnet_LookupHost_send()` is a shortcut that forces `NBT_NAME_SERVER`. `libnet_LookupDCs_send()` maps the local workgroup name to the configured DNS domain, requests DCs with LDAP, DS, and writable flags using the configured netlogon ping protocol and optional `ctx->server_address`, and calls `finddcs_cldap_send()`. Receive returns one `nbt_dc_name` built from the CLDAP result address and PDC DNS name.

`libnet_LookupName_send()` ensures an LSA domain policy handle through `lsa_domain_opened()`, prepares a level-1 single-name `lsa_LookupNames` request, and sends it. Completion checks transport status, RPC result, and that returned SID count matches the requested name count. Receive constructs a full SID by adding the returned RID to the first referenced domain SID, then returns RID, SID type, SID pointer/string, and error string.

## State And Persistence Behavior
Lookup operations are read-only on remote systems. They may populate or reuse the cached LSA handle in `libnet_context` through the domain-open prerequisite. Results are allocated under the caller memory context. No local persistent storage is written.

## Dependencies And Integration Points
Dependencies include composite contexts, Samba resolve subsystem, finddc/CLDAP helpers, credentials/loadparm for DC discovery, generated LSA RPC bindings, security SID helpers, and `libnet_DomainOpen` prerequisite helpers. Group information uses `libnet_LookupName()` to translate group names before SAMR groupinfo.

## Risks
`LookupDCs` returns exactly one DC despite the plural API, reflecting `finddcs_cldap` output rather than a full list. Name lookup builds a SID only from the first referenced domain, which is appropriate for single-name lookup but would not generalize to multiple names. `Lookup_recv()` returns no error string in its structure. Null or missing domain/SID arrays can produce success with no SID when count is zero, so callers must inspect outputs.

## Test Signals
Tests should cover invalid hostname parameter handling, caller-provided vs context resolve context, host shortcut name type, workgroup-to-DNS-domain mapping in DC lookup, writable LDAP/DS DC filtering, LSA domain-open prerequisite paths, no-match lookup returning success with empty outputs, malformed SID-count response rejection, and integration with group lookup.
