# sources/user-network-fs/samba/source4/rpc_server/lsa/dcesrv_lsa.c

## Purpose

`dcesrv_lsa.c` is the main Samba4 LSARPC endpoint implementation. It supplies most generated NDR server handlers for `lsarpc`, plus the remaining `dssetup` role query endpoint that depends on LSA policy state. The file handles LSA policy information queries, privilege and account-right enumeration/mutation, trusted-domain object lifecycle, secret storage, forest trust information, and server registration for LSARPC and DSSETUP.

The file relies on `lsa_init.c` for policy handle construction and on `lsa_lookup.c` for name/SID lookup calls. It includes `ndr_lsa_s.c` and `ndr_dssetup_s.c` to bind the static handler names into the generated RPC dispatch tables, then exports `dcerpc_server_lsa_init()` to register both endpoint servers.

## Important APIs, Types, and Functions

- `struct lsa_account_state`, `struct lsa_secret_state`, and `struct lsa_trusted_domain_state` are per-handle private state objects stored in `struct dcesrv_handle`.
- `dcesrv_interface_lsarpc_init_server()` optionally registers LSARPC on the Netlogon pipe when `lsa over netlogon` is enabled, then delegates to generated server init.
- `dcesrv_lsa_QueryInfoPolicy2()` returns domain, DNS, audit, quota, and role policy info from `lsa_policy_state`.
- `dcesrv_dssetup_DsRoleGetPrimaryDomainInformation()` maps Samba server role and domain state into DSSETUP role responses.
- Account and privilege handlers create/open account handles, enumerate account SIDs with privileges, list and modify privilege DB rights, translate privilege names/LUIDs, and report system-access right bits.
- Trusted-domain handlers create, open, query, enumerate, update, and delete trustedDomain records and associated inbound trust users.
- Secret handlers create/open/delete, set, and query global and local LSA secrets.
- Forest trust handlers query and set `msDS-TrustForestTrustInfo` with validation and collision reporting.
- Trust authentication helpers decrypt RC4/session-key and AES/HMAC auth blobs and repack incoming/outgoing trust password arrays.

## Control Flow

RPC entry points generally validate transport or pull a typed handle via `DCESRV_PULL_HANDLE()`. Policy calls unwrap `LSA_HANDLE_POLICY`; account, secret, and trusted-domain calls unwrap their matching handle type. Output pointers are usually initialized before validation.

Trusted-domain creation flows through a precheck and common create function. The precheck rejects invalid names/SIDs, conflicting trust attributes, unsupported within-forest/PIM trust creation, current-domain and BUILTIN collisions, and oversized NetBIOS names. The common function decodes auth blobs, checks for duplicate TDOs, creates the TDO under the System container, optionally writes default forest trust info, optionally creates an inbound interdomain trust user, commits an LDB transaction, and returns a trusted-domain handle.

Trusted-domain updates flow through `setInfoTrustedDomain_base()`, which decodes the requested info level, verifies that the requested DNS/NetBIOS/SID tuple still names the target TDO, blocks trust type changes, permits only limited trust attribute changes, toggles auth blobs, updates or deletes the interdomain trust user when inbound direction changes, and commits all DB changes in one transaction.

Secret operations split on names prefixed with `G$`. Global secrets are AD `secret` objects in the System container accessed through a system SAMDB connection; local secrets are in `secrets.ldb` under `cn=LSA Secrets`. `SetSecret()` decrypts incoming values with the transport session key, rotates prior/current values and timestamps, and uses `dsdb_replace()`. `QuerySecret()` reads selected values and encrypts them with the session key before returning.

Forest trust set/query requires the current domain to be the forest root. Set additionally requires the server to be PDC, normalizes supplied records, checks collisions against local xref and other TDOs, supports check-only mode, and writes normalized forest trust info only for non-check-only calls.

## State and Persistence Behavior

Persistent state is held in `sam.ldb` for domain metadata, trustedDomain objects, global secrets, interdomain trust users, and forest trust blobs; in the privilege DB for account rights keyed by `objectSid`; and in `secrets.ldb` for non-global secrets. Handles are transient server-side objects that hold policy/account/secret/trusted-domain state.

Trusted-domain create, delete, and update paths use transactions when multiple records can change together. Secret updates use DSDB replace semantics. LSA account objects themselves are mostly handle-only; account rights are the durable data.

## Dependencies and Integration Points

The file integrates with Samba DCERPC handles and generated NDR server glue, SAMDB/DSDB helpers, the privilege DB, security descriptor helpers, Kerberos/KDC policy helpers, GnuTLS crypto, trust-routing and forest-trust utilities, session-key encryption helpers, and loadparm server-role configuration. It consumes `lsa_policy_state` and handle tags from `lsa.h`.

## Risks and Edge Cases

- Access checks are incomplete or coarse in places: trusted-domain open has a TODO, and account handle creation grants requested access before later DB operations decide success.
- RC4 trust auth handling is sensitive to weak-crypto policy and transport encryption; Ex3 AES handling has different validation rules.
- Secret APIs expose credential material if authorization or session-key encryption is wrong.
- Trusted-domain mutation intentionally rejects many attribute changes; expanding it requires careful compatibility and rollback testing.
- Forest trust set is PDC-only and collision-sensitive.
- Many RPC operations deliberately fault with `DCERPC_FAULT_OP_RNG_ERROR`; generated IDL drift could accidentally expose unsupported behavior.

## Test Signals

Strong signals include RPC torture coverage for policy query/open/close, account rights and privileges, secret lifecycle with admin and non-admin callers, trusted-domain create/open/query/set/delete, inbound trust user creation/removal, forest trust collision reporting and check-only behavior, endpoint registration with `lsa over netlogon`, invalid handles/transports, weak-crypto-disabled trust auth, and expected unsupported-op faults.
