# sources/user-network-fs/samba/source3/passdb/pdb_samba_dsdb.c

## Purpose
`pdb_samba_dsdb.c` implements the `samba_dsdb` and legacy alias `samba4` passdb backends. It adapts the source3 `struct pdb_methods` interface directly onto the Samba AD DSDB/SAM LDB database, so source3 passdb callers can read and mutate AD users, groups, aliases, SID/id mappings, account policies, and trusted-domain data without going through an LDAP server.

This backend is intended for AD DC-style deployments where `sam.ldb`, DSDB helper APIs, source4 authentication/session infrastructure, and idmap are available. It is not a full implementation of every historical passdb operation; several old mapping and rename hooks return `NT_STATUS_NOT_IMPLEMENTED`.

## Important APIs, Types, And Functions
The private state is `struct pdb_samba_dsdb_state`, which holds a tevent context, `struct ldb_context *ldb`, `struct idmap_context *idmap_ctx`, and source4 `loadparm_context`. `pdb_init_samba_dsdb()` allocates this state, creates source4 event/loadparm contexts, connects to `sam.ldb` or a supplied URL via `samdb_connect_url()`, initializes idmap, synchronizes domain SID/GUID into secrets, and installs the passdb method table. `pdb_samba_dsdb_init()` registers the backend as both `samba_dsdb` and `samba4`.

User lookup is centered on `pdb_samba_dsdb_getsamupriv()`, `pdb_samba_dsdb_getsampwfilter()`, `pdb_samba_dsdb_getsampwnam()`, and `pdb_samba_dsdb_getsampwsid()`. `pdb_samba_dsdb_init_sam_from_priv()` translates LDB attributes into `struct samu`: account name, timestamps, display/home/profile fields, user parameters, object SID, account flags, password hashes, and primary group SID. `pdb_samba_dsdb_replace_by_sam()` is the reverse translator for updates, building DSDB modify messages and using special controls for password hashes and password last-set behavior.

User lifecycle methods include `pdb_samba_dsdb_create_user()`, `pdb_samba_dsdb_delete_user()`, `pdb_samba_dsdb_add_sam_account()`, `pdb_samba_dsdb_update_sam_account()`, and `pdb_samba_dsdb_delete_sam_account()`. Group and alias methods include `pdb_samba_dsdb_getgrfilter()`, `getgrsid/getgrgid/getgrnam`, `create_dom_group`, `delete_dom_group`, `enum_group_members`, `enum_group_memberships`, `create_alias`, `delete_alias`, `add_aliasmem`, `del_aliasmem`, `enum_aliasmem`, and `enum_alias_memberships`.

SID/id mapping is delegated to source4 idmap through `pdb_samba_dsdb_id_to_sid()` and `pdb_samba_dsdb_sid_to_id()`. Search APIs are implemented by `pdb_samba_dsdb_search_filter()` and `search_users/search_groups/search_aliases`, which materialize `samr_displayentry` arrays from DSDB searches. Trust APIs are extensive: old passdb trust password functions (`get_trusteddom_pw`, `get_trusteddom_creds`, `set_trusteddom_pw`, `enum_trusteddoms`) and newer `pdb_trusted_domain` lifecycle functions (`get_trusted_domain`, `get_trusted_domain_by_sid`, `set_trusted_domain`, `del_trusted_domain`, `enum_trusted_domains`, `filter_hints`).

## Control Flow
Initialization builds a method table in `pdb_samba_dsdb_init_methods()`. The module then connects to DSDB as the system session, creates idmap state, and calls `pdb_samba_dsdb_init_secrets()` to ensure the source3 secrets database has protected copies of the AD domain SID and GUID. Failure during any step frees the method instance and prevents registration from producing a usable backend.

For reads, callers invoke passdb lookup by name or SID. The backend formats an LDAP-style filter, runs `dsdb_search_one()` under the default base DN with a fixed attribute set, and maps the returned LDB message into `struct samu`. The LDB message is attached as backend-private data on the `samu`, allowing later updates to use the original DN without another lookup.

For user creation with a populated `samu`, `pdb_samba_dsdb_add_sam_account()` starts an LDB transaction, calls `dsdb_add_user()` with selected account control bits and any caller-supplied SID, then applies all set/changed `samu` fields through `pdb_samba_dsdb_replace_by_sam()`. Normal updates call the same replacement helper with `pdb_element_is_changed`. Password updates take one of two paths: cleartext passwords are converted to UTF-16 and written as `clearTextPassword`; direct LM/NT hashes and history use DSDB bypass controls and delete related attributes to avoid inconsistent credentials.

Group and alias operations mostly translate passdb RIDs/SIDs into DSDB DNs of the form `<SID=...>`. Membership modifications create a modify message for the `member` attribute and map LDB duplicate/missing-value errors to membership NTSTATUS values. Group membership enumeration reads DSDB group members or tokenGroups and maps each SID to a GID via idmap; failures to map group SIDs are hard errors because missing deny-group mappings could weaken ACL evaluation.

Trust password retrieval searches a trustedDomain object, validates outbound trust direction and trust type, parses `trustAuthOutgoing` as `trustAuthInOutBlob`, then extracts either cleartext UTF-16 password material or NT OWF hashes into legacy strings or `cli_credentials`. Setting an outbound trust password is restricted to the PDC, increments the version element, moves current auth data to previous, writes a new cleartext auth entry plus version entry, and commits it in one transaction.

Full trusted-domain creation validates the target SID and names, ensures the DC is PDC, confirms no existing TDO, creates the `trustedDomain` object under the system container, stores trust auth blobs and metadata, and for inbound trusts also creates an interdomain trust user account with a DSDB control that permits the UAC. Deletion removes the TDO and, for inbound trusts, deletes the corresponding trust user only if it is actually an interdomain-trust account.

## State And Persistence
Persistent state lives primarily in AD DSDB/LDB: users, groups, aliases, memberships, passwords, password history, trustedDomain objects, trust auth blobs, interdomain trust user accounts, and sequence numbers. The backend also writes domain SID and GUID into source3 secrets with protection flags so source3 components can find local domain identity without linking to DSDB directly.

Runtime state consists of the passdb method instance, its private DSDB/idmap/loadparm/event contexts, backend-private LDB messages attached to `struct samu`, temporary talloc stack frames, and transaction state around multi-step mutations. Account policy reads and writes are delegated to the shared account policy backend, not stored directly by this file.

The backend advertises `PDB_CAP_STORE_RIDS`, `PDB_CAP_ADS`, and `PDB_CAP_TRUSTED_DOMAINS_EX`. `new_rid` deliberately returns false because RID allocation is owned by DSDB object creation, not by source3 passdb.

## Dependencies And Integration Points
This file integrates source3 passdb with source4 DSDB. It depends on `passdb.h`, `samdb.h`, LDB, DSDB common utilities, DSDB trust helpers, source4 event and auth session setup, source4 idmap, credentials, generated NDR types for security/DRS/LSA trust blobs, base64 helpers, LDAP NDR encoding, secrets helpers, and loadparm.

Important external APIs include `dsdb_add_user()`, `dsdb_add_domain_group()`, `dsdb_add_domain_alias()`, `dsdb_search_one()`, `dsdb_search()`, `dsdb_replace()`, `dsdb_enum_group_mem()`, `dsdb_expand_nested_groups()`, `dsdb_lookup_rids()`, `dsdb_trust_search_tdo*()`, `dsdb_trust_search_tdos()`, `dsdb_trust_local_tdo_info()`, `dsdb_trust_xref_forest_info()`, `idmap_sids_to_xids()`, `idmap_xids_to_sids()`, `samdb_result_*()`, `account_policy_get/set()`, and `cli_credentials_*()`.

The passdb interface is populated in `pdb_samba_dsdb_init_methods()`, making this file an adapter layer for smbd, net, rpc_server/samr, auth, and trust-management code paths that expect source3 passdb calls.

## Risks
Filter strings are built with formatted user/domain data in several places. Samba's LDB formatting helpers handle many cases, but malformed or unescaped names would be high-impact because these paths query privileged directory state. Password handling is sensitive: direct hash writes require DSDB bypass controls and delete supplemental credentials to avoid stale credential material; any missed flag can leave inconsistent password state.

Some passdb methods are intentionally unimplemented (`rename_sam_account`, login-attempt updates, group mapping entry mutation/enumeration, `lookup_names`, `set_unix_primary_group`, trust password deletion, and RID allocation). Callers must tolerate these gaps or use DSDB-native code paths. Membership enumeration treats idmap failures as access-critical errors, which is safer for ACLs but can break logons if idmap is misconfigured.

Trust code has high blast radius. It parses and rewrites opaque NDR blobs, enforces PDC-only updates in some but not all read paths, creates/deletes interdomain trust users, and must distinguish inbound/outbound and AD/MIT trust types correctly. `add_trust_user()` uses `taiob->count` while indexing `taiob->current.array`, so trust blob shape assumptions matter. Any change in DSDB trust schema or auth blob layout needs careful tests.

## Test Signals
Useful tests include AD DC passdb backend initialization against `sam.ldb`, user lookup by name/SID, create/update/delete of users with password hash and cleartext password changes, primary group changes, DSDB account-control mapping, search enumeration for users/groups/aliases, group and alias membership add/delete/enumeration, idmap failure behavior, account policy get/set, and sequence number retrieval.

Trust tests should cover outbound trust password retrieval as legacy password and `cli_credentials`, password rollover preserving previous auth data and version, PDC-only write rejection, invalid trust type/direction rejection, TDO create/delete including inbound trust user creation/removal, lookup by SID and name, forest trust filter hints, and malformed `trustAuthOutgoing` NDR blobs. Regression tests should also assert the documented `NT_STATUS_NOT_IMPLEMENTED` methods stay predictable to callers.
