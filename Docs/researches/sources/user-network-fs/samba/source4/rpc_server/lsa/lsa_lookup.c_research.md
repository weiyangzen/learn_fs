# sources/user-network-fs/samba/source4/rpc_server/lsa/lsa_lookup.c

## Purpose

`lsa_lookup.c` implements LSARPC name-to-SID and SID-to-name translation. It supports all exposed LookupSids and LookupNames variants, including handle-based named-pipe/local calls and handle-less secure TCP calls. Resolution is layered through local predefined, builtin, account-domain, and remote winbind/trust-routing views.

## Important APIs, Types, and Functions

- `struct dcesrv_lsa_TranslatedItem` stores one lookup item, resolved values, winbind index, completion flags, invalid SID marker, and parsed name hints.
- `struct dcesrv_lsa_Lookup_view` defines paired `lookup_sid` and `lookup_name` callbacks.
- `struct dcesrv_lsa_Lookup_view_table` maps lookup levels to ordered view lists.
- `dcesrv_lsa_lookup_name()` and `dcesrv_lsa_lookup_sid()` query SAMDB for one local account name or SID.
- `dcesrv_lsa_authority_list()` builds output `lsa_RefDomainList` entries without duplicating authorities.
- Shared base engines implement LookupSids and LookupNames call, finish, output mapping, and asynchronous winbind callbacks.
- Public handlers include `LookupSids`, `LookupSids2`, `LookupSids3`, `LookupNames`, `LookupNames2`, `LookupNames3`, and `LookupNames4`.
- `schannel_call_setup()` validates handle-less TCP calls and caches an implicit policy state on the connection.

## Control Flow

LookupSids variants normalize older and newer RPC shapes into an internal `lsa_LookupSids3` request. The base call validates the lookup level, allocates outputs, initializes one translated item per SID, records SID/RID hints, and iterates the selected view table. Views can resolve an item, mark invalid SID, ignore none/some mapped statuses, or return a real error. Unresolved remote items can trigger one asynchronous IRPC call to winbind. Finish builds authority domains, writes translated names, counts mapped items, and returns OK, `NONE_MAPPED`, `STATUS_SOME_UNMAPPED`, or `INVALID_SID`.

LookupNames follows the same pattern with an internal `lsa_LookupNames4` request. It parses `DOMAIN\principal`, `DOMAIN\`, UPN-style `principal@namespace`, isolated names, and null names into hints, validates lookup options, iterates views, optionally calls winbind, then maps common `TranslatedSid3` output back to older structures by deriving RID values and sid indexes.

`LookupSids3` and `LookupNames4` do not take policy handles. `schannel_call_setup()` requires `NCACN_IP_TCP` plus Kerberos privacy or schannel authentication, then creates or reuses a connection-cached policy state with access checks skipped.

View selection depends on lookup level: all views for `ALL`, account plus winbind for domain/global-catalog style levels, account-only for primary-domain-only, and winbind-only for forest-trust or RODC referral levels.

## State and Persistence Behavior

Lookup operations are read-only against SAMDB and trust-routing data. Per-call state is allocated under the request memory context. Handle-less secure TCP lookups cache an implicit `lsa_policy_state` on the DCERPC connection. Remote resolution uses an IRPC binding handle to `winbind_server` and marks the DCERPC call asynchronous until the callback maps results and sends `dcesrv_async_reply()`.

## Dependencies and Integration Points

Local lookup depends on SAMDB searches over domain and builtin DNs, account-type mapping via `ds_atype_map()`, predefined SID helpers, loadparm role/name matching, and trust routing APIs. Remote lookup integrates with Samba messaging/IRPC, generated LSA client bindings, winbind server lookup calls, and DCERPC async reply machinery.

## Risks and Edge Cases

- Protocol-compatible name parsing has many edge cases: null names, `DOMAIN\`, isolated names, UPN suffixes, predefined names, and lookup-option restrictions.
- Handle-less LookupSids3/LookupNames4 security depends on strict transport/auth checks.
- Winbind referral batching relies on correct per-item `wb_idx` mapping.
- Multiple-domain forest support is explicitly incomplete in TODOs.
- Status mapping is protocol-sensitive and depends on mapped counts and invalid SID markers.

## Test Signals

Test all LookupNames/LookupSids variants and lookup levels; predefined, BUILTIN, local domain, unknown, null, isolated, `DOMAIN\`, and UPN inputs; invalid SIDs; handle-less TCP calls with accepted and rejected auth; winbind success, partial mapping, timeout, and failure; trusted-domain routing including forest-trust-only and RODC referral levels; and old output structure RID/sid-index compatibility.
