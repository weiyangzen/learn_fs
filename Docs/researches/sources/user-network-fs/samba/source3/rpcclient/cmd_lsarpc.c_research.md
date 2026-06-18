# sources/user-network-fs/samba/source3/rpcclient/cmd_lsarpc.c

## Purpose
`cmd_lsarpc.c` implements the `rpcclient` LSARPC command set. It exposes interactive commands for querying policy information, translating SIDs and names, enumerating trusts and privileges, managing LSA accounts/account rights, reading security descriptors, managing trusted-domain records, and creating/querying/storing LSA secrets and private data. It is diagnostic and administrative glue around generated `lsa` DCE/RPC client stubs.

## Important APIs, types, and functions
- `name_to_sid()` accepts either a raw SID string or an account name and resolves it with `rpccli_lsa_lookup_names()` after `rpccli_lsa_open_policy()`.
- `display_query_info_*()` and `display_lsa_query_info()` format selected `union lsa_PolicyInformation` levels, including audit, account-domain, and DNS-domain information.
- Name/SID translation commands include `cmd_lsa_lookup_names`, `cmd_lsa_lookup_names_level`, `cmd_lsa_lookup_names4`, `cmd_lsa_lookup_sids`, `cmd_lsa_lookup_sids_level`, and `cmd_lsa_lookup_sids3`.
- Enumeration/query commands cover trusted domains, privileges, privilege display names, LSA accounts, account rights, privilege values, policy security descriptors, current username, and trusted-domain information by SID/name/handle.
- Mutating commands include account creation, adding/removing account rights, adding/removing privileges, setting trusted-domain encryption types, creating/deleting/updating secrets, storing private data, creating trusted domains through legacy/Ex2/Ex3 variants, and deleting trusted domains.
- Secret and trust-password paths use `dcerpc_binding_handle_transport_session_key()`, `sess_encrypt_string()`, `sess_decrypt_string()`, `rpc_lsa_encrypt_trustdom_info()`, and `rpc_lsa_encrypt_trustdom_info_aes()`.
- The exported `lsarpc_commands[]` table maps user command names to handlers with `RPC_RTYPE_NTSTATUS`, `&ndr_table_lsarpc`, descriptions, and a terminating null entry.

## Control flow
Most handlers parse `argv`, open an LSA policy handle with either `rpccli_lsa_open_policy()` or `dcerpc_lsa_open_policy_fallback()`, call one generated RPC operation on `cli->binding_handle`, validate both transport `status` and server `result`, print formatted results, and close policy handles. Translation commands intentionally accept `STATUS_SOME_UNMAPPED` as displayable partial success. Enumeration commands loop while the server returns `STATUS_MORE_ENTRIES`, carrying the resume context supplied by the RPC.

Trusted-domain commands open policy handles with maximum access, then either query directly by SID/name or open a trusted-domain handle before querying or setting information. Password-bearing trust info is decrypted for display with the negotiated transport session key. Secret and private-data commands open the policy/secret object, encrypt or decrypt payloads with the transport session key, and invoke `lsa_CreateSecret`, `OpenSecret`, `QuerySecret`, `SetSecret`, `RetrievePrivateData`, or `StorePrivateData`.

## State and persistence behavior
This file has no local persistent storage. It mutates remote LSA state through RPC: account rights and privileges, secret objects, private data values, and trusted-domain records are persisted by the target server. Local allocations are talloc-scoped to the command context. Policy and object handles are remote state and must be closed; most paths close them, often guarded by `is_valid_policy_hnd()`.

## Dependencies and integration points
The module depends on `rpcclient.h`, generated `ndr_lsa` structures/stubs, `rpc_client/cli_lsarpc.h`, `rpc_client/init_lsa.h`, SID/security helpers, session encryption helpers from `libcli_auth`, and `struct cmd_set` registration used by the rpcclient command dispatcher. It integrates with the active DCE/RPC binding and the authentication/session protection already established by rpcclient.

## Risks and edge cases
- Several commands print decrypted secrets or trust passwords to stdout, so captured terminal output can expose sensitive material.
- Many mutating commands request `SEC_FLAG_MAXIMUM_ALLOWED`, which is useful for diagnostics but high impact when run with privileged credentials.
- `cmd_lsa_enum_trust_dom()` checks `argc == 2` but reads `argv[2]`, an out-of-bounds argument access when a single optional resume context is provided.
- `cmd_lsa_create_secret()` opens policy into `sec_handle` but passes the uninitialized `handle` to `dcerpc_lsa_CreateSecret()`, suggesting a handle mix-up.
- Some handles are not closed on every error path, and some commands close only parent handles while child handles may remain open until connection teardown.
- Raw `atoi()`/`sscanf()` parsing gives little validation for info classes, access masks, trust directions, encryption types, and sizes.
- `CreateTrustedDomainEx2/Ex3` require enough arguments for both incoming and outgoing passwords, but the usage guard is `argc < 7` even though `argv[7]` is read.

## Test signals
Useful tests include rpcclient integration runs against a Samba test DC for `lsaquery`, `lookupnames`, `lookupsids`, partial unmapped translation, privilege enumeration, account-right add/remove round trips, and trust enumeration pagination. Negative tests should cover malformed SIDs, unsupported info classes, missing arguments for `enumtrust` and trust creation, unavailable session keys for secret/trust password display, and server-side access-denied responses. Secret/private-data tests should verify encrypted storage round trips without leaking values into logs unless explicitly requested by the command.
