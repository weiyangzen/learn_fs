# sources/user-network-fs/samba/source4/dsdb/samdb/cracknames.c

## Purpose
`cracknames.c` implements DRSUAPI `DsCrackNames()` style name translation for Samba AD DS. It converts between LDAP DNs, canonical names, NT4 names, GUIDs, display names, user principal names, service principal names, SIDs, and DNS-domain-like responses, and provides helper wrappers used by authentication/KDC code and DRS RPC handlers.

## Important APIs, types, and functions
- `DsCrackNameOneName()` is the central dispatcher. It builds domain and result LDAP filters for the offered format, handles syntactical-only requests, and delegates to `DsCrackNameOneFilter()`.
- `DsCrackNameOneFilter()` performs domain crossRef lookup, object search with the requested attributes, ambiguity handling, fallback for SPN aliases/UPN variants, and output formatting.
- `DsCrackNameOneSyntactical()` maps FQDN_1779 DNs to canonical or canonical-ex names without a database search.
- `DsCrackNameSPNAlias()` and `LDB_lookup_spn_alias()` implement service principal fallback through `sPNMappings` under `CN=Directory Service,CN=Windows NT,CN=Services,...`.
- `DsCrackNameUPN()` handles UPN fallback by parsing the Kerberos realm, locating the domain crossRef, and searching by unescaped `samAccountName`.
- `get_format_functional_filtering_param()` walks canonical path components to narrow searches for canonical/canonical-ex names.
- Public helpers include `crack_user_principal_name()`, `crack_service_principal_name()`, `crack_name_to_nt4_name()`, `crack_auto_name_to_nt4_name()`, `dcesrv_drsuapi_ListRoles()`, `dcesrv_drsuapi_CrackNamesByNameFormat()`, and `dcesrv_drsuapi_ListInfoServer()`.

Key types are `drsuapi_DsNameFormat`, `drsuapi_DsNameInfo1`, `drsuapi_DsNameCtr1`, `smb_krb5_context`, `ldb_context`, `ldb_dn`, `ldb_result`, `dom_sid`, and `GUID`.

## Control flow
For `DRSUAPI_DS_NAME_FORMAT_UNKNOWN`, `DsCrackNameOneName()` recursively tries a fixed ordered list of plausible formats and returns the first status that is not an ignorable not-found case. For known input formats, it parses the input and prepares a domain filter, a result filter, a direct DN, a search scope, and sometimes a Kerberos context. Canonical names split at `/` or newline, NT4 names split at `\`, GUID and SID formats are NDR-encoded for LDAP filters, display names search `displayName` or `samAccountName`, UPN/SPN formats use Kerberos parsing and LDAP-safe encoding.

`DsCrackNameOneFilter()` first resolves the domain crossRef when a domain filter exists. It then searches either all partitions for GCVERIFY/GUID, the resolved NC, the default NC, or a direct DN. Result count drives status: one result is formatted, zero may invoke SPN alias or UPN fallback, and multiple results usually become `NOT_UNIQUE` except canonical searches try exact canonical string matching before declaring ambiguity. Output formatting then returns the requested representation, including special handling for NT4 domain names, BUILTIN SIDs, canonical-ex synthesis, and single-valued SPN requirements.

The KDC-facing helpers crack UPN/SPN to FQDN_1779, validate status mapping to NTSTATUS, and optionally crack the DNS domain portion back to a domain DN. RPC entry points allocate result arrays and call the single-name cracker for each requested name.

## State and persistence behavior
This file does not persist directory state. It performs read-only LDB/DSDB searches and allocates result strings under caller-supplied talloc contexts. It may initialize Kerberos contexts and parse/free Kerberos principals. Status is returned in `drsuapi_DsNameInfo1` fields rather than by throwing errors for ordinary lookup failures.

## Dependencies and integration points
The implementation integrates with DRSUAPI RPC structures, LDB search APIs, DSDB search helpers and partition/crossRef layout, Kerberos principal parsing/unparsing, LDAP NDR encoders for GUID/SID filters, domain SID helpers, FSMO role helpers, and server/reference lookup for `ListInfoServer`. It is used by DRS RPC name cracking and by authentication/KDC paths that need to resolve principals to user/domain DNs.

## Risks and edge cases
- LDAP filter injection is mitigated by `ldb_binary_encode_string()` and NDR encoders; new formats must preserve that discipline.
- Kerberos unparsing flags intentionally use display/no-realm modes in specific cases so spaces and escaping match AD attributes.
- SPN alias behavior returns the first matching mapping and is documented as mirrored in `samldb.c`; changing ordering can break compatibility.
- Canonical parsing mutates temporary strings while walking path components and must distinguish domain-only from object searches.
- Result status semantics are subtle: many search or parse failures return `WERR_OK` with a DS name status, while internal allocation/configuration errors return WERROR failures.
- GUID searches include recycled objects and may search all partitions, which is important for deleted-object behavior.

## Test signals
Coverage should include each offered and desired format pair used by DRS clients, syntactical-only DN-to-canonical mapping, unknown-format fallback ordering, NT4 domain/user and BUILTIN handling, UPN with escaped spaces and alternate realm lookup, SPN host/computer fallback, SPN alias mappings, duplicate result `NOT_UNIQUE`, domain-only responses, GCVERIFY/all-partition search, SID/GUID encoding, KDC helper NTSTATUS mappings, `ListRoles`, and `ListInfoServer`.
