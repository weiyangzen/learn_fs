# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/acl.c

## Purpose
`acl.c` is Samba's main DSDB LDB ACL enforcement module for write-side operations and selected search-time constructed attributes. It checks add, modify, delete, rename, and extended operations against the caller security token and object security descriptors, implements validated writes for sensitive attributes, handles password-change/reset ACL classification, and synthesizes AD-style constructed attributes such as `allowedAttributesEffective`.

## Important APIs, types, and functions
- `acl_module_init()` installs module private state, reads `acl:search`, and registers the SD flags control.
- Constructed attribute helpers: `acl_allowedAttributes()`, `acl_childClasses()`, `acl_childClassesEffective()`, and `acl_sDRightsEffective()`.
- Validated write helpers: `acl_check_spn()`, `acl_validate_spn_value()`, `acl_check_dns_host_name()`, `acl_check_ms_ds_key_credential_link()`, and `acl_check_self_membership()`.
- Operation gates: `acl_add()`, `acl_modify()`, `acl_delete()`, `acl_rename()`, `acl_extended()`, and `acl_search()`.
- Password flow: `acl_check_password_rights()`, `copy_password_acl_validation_control()`, and `acl_callback()`.
- Confidential search fallback: `acl_search_update_confidential_attrs()` and `acl_search_callback()`.

Main state structures are `acl_private` for module-level configuration and confidential-attribute cache, and `acl_context` for per-search state including requested constructed attributes, system/admin booleans, and schema pointer.

## Control flow
Initialization creates `acl_private`, stores whether `acl:search` is enabled, registers SD flags, then initializes the next module. Most operation handlers skip special DNs and callers with system access.

`acl_add()` determines the new object's structural class, checks create-child rights on either the parent or `CN=Partitions`/crossRef path for NC heads, then optionally performs per-attribute authorization using the calculated default security descriptor. Mandatory attributes and password attributes are treated specially. Computer-derived adds validate SPN, DNS host name, key credential link, self-membership, SACL privilege, and write-DAC/write-property rights against the default SD.

`acl_modify()` reads the target object's SD, object classes, and SID as system, then checks each modified attribute. It maps `nTSecurityDescriptor` SD flags to write-owner/write-DAC/system-security access, applies implicit-owner rules and computer-owner blocking, routes password attributes through `acl_check_password_rights()`, validates SPN/DNS/key credential changes, allows undelete-specific `isDeleted`, and otherwise requires write-property on the attribute. It wraps the downstream modify with `acl_callback()` so password ACL validation metadata is copied to the reply for audit logging.

`acl_delete()` forbids deleting NC roots, then accepts either delete-tree, delete-object on the object, or delete-child on the parent. `acl_rename()` forbids moving/renaming NC roots, handles tombstone reanimation via an extended right on the NC root, requires write-property on `name` and the old RDN attribute, and for moves requires create-child on the new parent plus delete-object or delete-child on the old location.

`acl_search()` is not the main read ACL path; it exists for constructed attributes and for confidential-attribute filter redaction when `acl:search` is disabled. It may rewrite confidential attributes in the parse tree to `kludgeACLredactedattribute`, then `acl_search_callback()` fills constructed attributes and strips confidential attributes from non-system/non-admin result entries.

`acl_extended()` only allows sequence-number reads to everyone. Other extended operations require system or administrator privileges.

## State and persistence behavior
The module itself persists no directory data directly; it authorizes or rejects requests before passing them down the LDB stack. It mutates request controls by marking handled controls non-critical and adds `DSDB_CONTROL_PASSWORD_ACL_VALIDATION_OID` for downstream password hashing/audit modules. Per-module state caches confidential attribute names keyed by schema pointer and metadata USN. Per-request talloc contexts own temporary SDs, schema data, search results, and callbacks.

## Dependencies and integration points
`acl.c` depends on DSDB schema lookup, SD parsing, `sec_access_check_ds` wrappers from `acl_util.c`, auth session tokens, objectclass sorting, validated-write extended rights under `CN=Extended-Rights`, Kerberos parsing for SPN validation, key credential NDR parsing, tombstone restore controls, calculated default SD controls, password hash/change controls, audit logging controls, and the surrounding LDB module stack.

## Risks and edge cases
- Validated writes are security-sensitive: SPN, DNS host name, self-membership, and key credential link checks must stay aligned with Windows semantics and objectclass constraints.
- Password modification classification is subtle and intentionally delegates malformed cases to `password_hash` by withholding the validation control.
- SD write checks depend on SD flags and implicit owner rights; computer-object blocking of owner implicit write-DAC is especially compatibility-sensitive.
- `DSDB_CONTROL_FORCE_ALLOW_VALIDATED_DNS_HOSTNAME_SPN_WRITE_OID` bypasses normal checks for selected updates and must remain tightly scoped.
- Constructed attribute generation performs extra system reads; missing schema or malformed objectClass/SD data becomes operational failure.
- Search-time confidential rewrite is a fallback when `acl_read` is not handling search ACLs; parser rewrites must avoid exposing confidential values through filters.

## Test signals
Useful tests include create-child and crossRef/NC-head add authorization, per-attribute add checks with calculated default SDs, SACL privilege enforcement, password change versus reset controls and audit response controls, SPN and DNS validated writes including deletes and DC-specific SPNs, `msDS-KeyCredentialLink` SELF/new-value constraints, self-membership modification, SD owner/DACL/SACL write flags, delete object/delete child/delete tree, rename versus move, tombstone reanimation right, constructed attributes for system/admin/non-admin callers, confidential attribute redaction when `acl:search` is disabled, and extended operation denial for non-admin callers.
