# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/acl_read.c

## Purpose
`acl_read.c` is the DSDB LDB module that enforces authorization on LDAP/search read results. It decides whether objects are visible, redacts attributes the caller cannot read, treats password/secret attributes as inaccessible, handles SD flag semantics, and registers a filter-redaction callback so inaccessible attributes used in search filters cannot be used as an oracle.

## Important APIs, types, and functions
- `aclread_search()` prepares downstream search requests by adding internal attributes needed for access checks and installing `DSDB_CONTROL_ACL_READ_OID`.
- `aclread_callback()` checks object visibility, attribute visibility, removes internally added attributes, and sends filtered entries.
- `aclread_check_object_visible()` and `aclread_check_parent()` implement List Children/List Object visibility semantics with a per-search parent cache.
- `aclread_get_sd_from_ldb_message()` parses and module-caches security descriptors by exact binary blob.
- `setup_access_check_context()` obtains schema, SD, structural class, and SID for per-attribute access checks.
- `acl_redact_attr()` checks secret/confidential/read-property access and marks inaccessible attributes.
- `acl_redact_msg_for_filter()` checks attributes referenced in a search parse tree before filter evaluation.
- `aclread_init()` loads secret/password attribute names from `@KLUDGEACL`, adds built-in secret attributes, sorts them, registers the redaction callback, and handles `userPassword` support.

Important structures are `aclread_context` for per-search state, `aclread_private` for module state and SD/password caches, `access_check_context`, and the sorted `ldb_attr_vec` used for filter attribute collection.

## Control flow
On search, the module skips if disabled, system, trusted/internal, or special DN. Otherwise it creates an `aclread_context`, computes SD flags from the request, and augments the requested attribute list with `instanceType`, `objectSid`, `objectClass`, and/or `nTSecurityDescriptor` when needed for ACL checks. It checks base-object visibility up front; an invisible base returns `NO_SUCH_OBJECT` for base scope or defers that result for subtree/onelevel searches that may still return visible children. The downstream request carries `DSDB_CONTROL_ACL_READ_OID`, allowing the filter redaction callback and reply callback to share state.

For each returned entry, `aclread_callback()` first verifies object visibility. NC heads are always visible. Otherwise the parent needs `SEC_ADS_LIST`, or when `dSHeuristics` enables List Object mode, the parent and object both need `SEC_ADS_LIST_OBJECT`. It then scans attributes. Attributes added only for ACL processing are marked inaccessible; already checked filter attributes are skipped; remaining attributes trigger setup of schema/SD/class/SID context and then `acl_redact_attr()`. After marking, `ldb_msg_remove_inaccessible()` physically strips hidden elements before sending the entry.

`acl_redact_msg_for_filter()` runs earlier in the LDB stack for candidate messages. It collects attributes referenced by the search parse tree, ignoring always-present/always-visible cases, and redacts those attributes before filter matching if the caller lacks rights. This prevents matching on secret/confidential/inaccessible attributes and then inferring their values from object presence.

## State and persistence behavior
The module persists no database changes. It mutates search requests by adding internal attributes and controls and mutates result messages in memory by marking/removing inaccessible attributes. Module-private state caches the last parsed security descriptor and its blob, plus a sorted array of password/secret attribute names. Per-search state caches schema, parent visibility result, requested SD flags, base invisibility, entry count, and collected filter attributes.

## Dependencies and integration points
It depends on auth session/security tokens, `acl_util.c` access-check helpers, DSDB schema and structural objectclass resolution, NDR security descriptor parsing, `@KLUDGEACL` passwordAttribute data, `DSDB_SECRET_ATTRIBUTES`, `dsdb_do_list_object()` dSHeuristics behavior, LDB SD flags control, `DSDB_CONTROL_ACL_READ_OID`, and the LDB redaction callback mechanism.

## Risks and edge cases
- Filter redaction only covers attributes visible in the parse tree; comments explicitly warn that extended match rules inspecting other attributes need their own ACL checks.
- SD parsing is cached by exact blob; callers must not retain the returned SD beyond the next cache update on the module context.
- Always-present and always-visible exceptions are intentional compatibility/security tradeoffs, especially `objectClass=*` visibility under List Children.
- `nTSecurityDescriptor` access depends on requested SD flags: owner/group/DACL require read-control, SACL requires system-security.
- Secret attributes are always hidden regardless of ordinary read-property rights.
- Request attribute augmentation must be removed from results to avoid leaking internal attributes the client did not request.

## Test signals
Test with normal LDAP searches as non-admin users over base, onelevel, and subtree scopes; invisible base behavior; List Children versus List Object dSHeuristics; NC head visibility; attribute redaction for ordinary, confidential, secret, and `nTSecurityDescriptor` attributes with SD flags; filter matching on inaccessible attributes; objectClass/name/objectGUID presence exceptions; system/trusted bypass; `userPassword` secret behavior toggled by support setting; and repeated entries sharing SDs to exercise cache behavior.
