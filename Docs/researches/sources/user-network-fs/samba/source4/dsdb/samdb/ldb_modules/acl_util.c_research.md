# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/acl_util.c

## Purpose
`acl_util.c` provides shared helper routines for DSDB ACL modules. It extracts the caller token, performs object/DN and attribute/class access checks, resolves extended rights and validated writes, parses SD flags controls, formats the caller name, and schedules security descriptor propagation.

## Important APIs, types, and functions
- `acl_user_token()` returns the current session security token from the LDB opaque `DSDB_SESSION_INFO`.
- `dsdb_module_check_access_on_dn()` reads an object's SD/SID as system through the module stack and calls `dsdb_check_access_on_dn_internal()`.
- `acl_check_access_on_attribute_implicit_owner()` builds an object tree for class, attributeSecurityGUID, and attribute schemaIDGUID, then calls `sec_access_check_ds_implicit_owner()`.
- `acl_check_access_on_attribute()` is the normal read/write property wrapper using default implicit-owner read-control rights.
- `acl_check_access_on_objectclass()` checks class-level rights such as create child/delete tree.
- `acl_check_extended_right()` verifies an extended right applies to the structural objectclass and then checks the right GUID in the security descriptor.
- `dsdb_request_sd_flags()` consumes the LDAP SD flags control and normalizes the four SECINFO bits.
- `dsdb_module_schedule_sd_propagation()` invokes `DSDB_EXTENDED_SEC_DESC_PROPAGATION_OID` as system/trusted/top-module.

## Control flow
DN-level checks fetch `nTSecurityDescriptor` and `objectSid` using `dsdb_module_search_dn()` with next-module, as-system, and show-recycled flags, then delegate to the internal SD access checker. Attribute checks construct a DS object tree rooted at the structural class GUID, optionally include the attribute security property-set GUID, and then the concrete attribute GUID; this lets DS ACLs grant rights at class, property set, or attribute level. Objectclass checks build a simpler class GUID tree.

Extended right checks first locate `CN=Extended-Rights`, search one level for the requested `rightsGuid` with an `appliesTo` value matching the structural class schemaIDGUID, convert the GUID string, build an object tree for that right, and call `sec_access_check_ds()`. SD flags parsing marks the request control non-critical once handled, masks to the low four bits, and treats zero bits as all owner/group/DACL/SACL bits per MS-ADTS.

## State and persistence behavior
These helpers do not persist ordinary directory changes. They allocate temporary object trees and search results under caller contexts. `dsdb_request_sd_flags()` mutates the request control criticality to indicate it has been handled. `dsdb_module_schedule_sd_propagation()` schedules persistent downstream SD propagation through an extended operation.

## Dependencies and integration points
The file integrates with `acl.c` and `acl_read.c`, auth/session info, LDB controls, DSDB module search and extended APIs, security descriptor access-check functions, object tree construction, schema class/attribute GUIDs, Extended-Rights container layout, and SD propagation extended operation infrastructure.

## Risks and edge cases
- Missing `DSDB_SESSION_INFO` or token generally produces operational failure; callers must ensure module context is initialized with session info.
- Attribute access depends on correct schema metadata, especially `attributeSecurityGUID` and `schemaIDGUID`.
- Extended rights require both an `appliesTo` directory object and an ACE granting the right; missing appliesTo is treated as insufficient access.
- `dsdb_request_sd_flags()` consumes the SD flags control; multiple modules must agree on that convention.
- Propagation scheduling uses trusted/system flags and should only be called after authorization has already succeeded.

## Test signals
Tests should cover object DN access checks, class create/delete checks, attribute checks granted via class GUID/property set/attribute GUID, implicit owner variants, extended rights with and without appliesTo, SD flags control normalization including zero flags, missing session info failure, recycled object lookup, and SD propagation extended operation invocation.
