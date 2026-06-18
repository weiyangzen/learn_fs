# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/operational.c

## Purpose

`operational.c` implements the Samba DSDB LDB `operational` module. It intercepts LDAP searches and makes Active Directory operational and constructed attributes appear with Windows-compatible behavior without storing most of them directly. It rewrites filters for searchable aliases such as `createTimeStamp` and `modifyTimeStamp`, expands requested attribute lists with hidden dependencies, post-processes returned entries, strips sensitive or helper attributes, and constructs values such as `tokenGroups`, `parentGUID`, `msDS-isRODC`, `msDS-KeyVersionNumber`, `msDS-User-Account-Control-Computed`, `msDS-UserPasswordExpiryTimeComputed`, `msDS-ResultantPSO`, and `msDS-ManagedPassword`.

The module is read-path focused. It registers only `.search` and `.init_context` handlers and depends on surrounding write-side modules to maintain stored attributes such as `whenCreated`, `whenChanged`, `objectSid`, `primaryGroupID`, `pwdLastSet`, `lockoutTime`, `replPropertyMetaData`, and PSO links.

## Important APIs, Types, and Tables

`struct operational_data` stores lazy module state, currently the aggregate schema DN used for `subSchemaSubEntry` and the schema aggregate special case for `modifyTimeStamp`.

`struct operational_context` is per-search state: original request, search scope, requested attrs, possibly rewritten parse tree, control flags, lists of attributes to remove and construct, cached smart-card password-expiry policy, and a cached current time.

`enum search_type` controls group SID expansion for `tokenGroups`, global/universal token groups, no-GC-acceptable token groups, and account groups used by PSO lookup.

`struct op_attributes_replace` and the `search_sub[]` table are the main behavior map. For each constructed/alias attribute, the table declares the requested attribute name, the backend replacement attribute if any, extra dependencies to fetch, and an optional constructor. `operational_search()` uses this table to expand the downstream request, and `operational_search_post_process()` uses it to add final attributes.

`operational_remove[]` defines attributes to remove from results. It always removes synthetic `parentGUID`, conditionally hides `nTSecurityDescriptor`, hides `msDS-KeyVersionNumber` unless bypass-operational control allows it, and removes replication metadata and DSDB secret attributes unless explicitly requested.

Key constructors include `construct_canonical_name()`, `construct_primary_group_token()`, `construct_token_groups*()`, `construct_parent_guid()`, `construct_modifyTimeStamp()`, `construct_subschema_subentry()`, `construct_msds_isrodc()`, `construct_msds_keyversionnumber()`, `construct_msds_user_account_control_computed()`, `construct_msds_user_password_expiry_time_computed()`, `construct_resultant_pso()`, and the imported `constructed_msds_managed_password()`.

PSO support is split across `pso_is_supported()`, `get_pso_count()`, `pso_search_by_sids()`, `pso_find_best()`, and `get_pso_for_user()`. Group SID expansion is centralized in `get_group_sids()` via `dsdb_expand_nested_groups()`.

## Control Flow

`operational_search()` is entered for normal searches, but special DNs bypass the module. The function allocates an `operational_context`, checks the filter parse tree for searchable operational aliases, and shallow-copies/replaces the parse tree only when needed. It records whether `LDB_CONTROL_SD_FLAGS_OID` and `LDB_CONTROL_BYPASS_OPERATIONAL_OID` are present.

It then walks the requested attribute list. If a requested attribute matches `search_sub[]`, the module records a replacement operation, adds any dependency attributes to the downstream attribute list, and substitutes the stored backend attribute where applicable. This is performance-sensitive: the table order intentionally allows `msDS-ResultantPSO` to be constructed before other attributes that can reuse it.

The downstream request is built with `ldb_build_search_req_ex()` and `operational_callback()`. For every entry, the callback calls `operational_search_post_process()`, which first removes attributes selected by `operation_get_op_list()`, then constructs requested attributes through constructors or by copying replacement attrs, and finally removes helper attrs that were added only to make construction possible unless the caller explicitly requested them or requested `*`.

Constructed attributes often perform additional internal searches. Examples: `construct_parent_guid()` checks whether the object is an NC head and searches the parent for `objectGUID`; `construct_msds_isrodc()` walks nTDSDSA/server/computer relationships; PSO-backed password/lockout attributes inspect direct PSO application, group membership, and the Password Settings Container.

## State and Persistence Behavior

The module persists no database state. Its only module-private state is the lazily cached aggregate schema DN. Per-request state is talloc-owned by the request. Expensive values such as the current time and `msDS-ExpirePasswordsOnSmartCardOnlyAccounts` are cached only for the lifetime of one search request.

Even though it does not write state, it interprets persistent DSDB state heavily: domain functional level, password policies, PSO objects, replicated property metadata, group memberships, security descriptors, schema timestamps, and gMSA managed-password material.

## Dependencies and Integration Points

The module integrates with the LDB module chain through `ldb_build_search_req_ex()`, `ldb_next_request()`, `ldb_module_send_entry()`, referrals, and module completion callbacks. It relies on DSDB helper APIs from `samdb.h`, `util.h`, managed password construction, NDR parsing of `replPropertyMetaDataBlob`, SID helpers from auth/security code, and schema/domain helpers such as `dsdb_functional_level()`, `dsdb_find_nc_root()`, `samdb_aggregate_schema_dn()`, and `dsdb_gmsa_current_time()`.

LDAP controls are important integration points. `LDB_CONTROL_SD_FLAGS_OID` changes whether `nTSecurityDescriptor` is retained. `LDB_CONTROL_BYPASS_OPERATIONAL_OID` allows direct exposure of `msDS-KeyVersionNumber`.

## Risks and Edge Cases

Constructed attributes are easy to break by changing dependency lists. Missing `objectClass`, `objectSid`, `primaryGroupID`, `pwdLastSet`, `userAccountControl`, or PSO fields can silently produce no value or fall back to domain defaults.

`tokenGroups` requires BASE scope; broader searches return operations errors if the attribute is requested. Group expansion and PSO lookup can be expensive and may recursively search large memberships.

The parse-tree replacement logic only covers attributes in `parse_tree_sub[]`; constructed attributes that are not searchable remain post-processing only. Shallow parse-tree copies and talloc references rely on the original request tree remaining alive.

Password expiry and lockout calculations depend on negative AD interval semantics and boundary handling for `INT64_MIN`/`INT64_MAX`. Small arithmetic mistakes here would create security-visible account-state bugs.

`msDS-KeyVersionNumber` depends on parsing replication metadata and a hard-coded `DRSUAPI_ATTID_unicodePwd` lookup. Corrupt metadata can turn a search into an operational error.

Secret-attribute hiding is centralized in `operational_remove[]`; additions to DSDB secret attributes must continue to flow into this list.

## Test Signals

Relevant tests should cover searching by `createTimeStamp`/`modifyTimeStamp` filters, requested constructed attributes with and without `*`, SD flags behavior, bypass-operational behavior for key version number, token group BASE-scope enforcement, parentGUID on NC heads and non-NC children, RODC detection across nTDSDSA/server/computer paths, PSO precedence and GUID tie-breaking, smart-card-only password expiry policy at functional levels below and at 2016, lockout duration fallback to domain defaults, and secret attribute suppression. Regression tests should verify helper attributes added for construction are stripped unless explicitly requested.
