# sources/user-network-fs/samba/source4/dsdb/common/dsdb_access.c

## Purpose
`dsdb_access.c` provides utility functions for checking access to DSDB objects outside the normal LDB module stack. It retrieves security descriptors, builds optional object-specific access trees, runs Windows-style security descriptor checks, and emits detailed debug output for grant/deny decisions.

## Important APIs, Types, and Functions
- `dsdb_acl_debug()` logs the DN, security token, and security descriptor.
- `dsdb_get_sd_from_ldb_message()` extracts and NDR-decodes `nTSecurityDescriptor` from an LDB message.
- `dsdb_check_access_on_dn_internal()` evaluates a supplied search result/security descriptor against a token, access mask, optional GUID, and object SID.
- `dsdb_check_access_on_dn()` searches the target DN as system for `nTSecurityDescriptor` and `objectSid`, parses an optional extended-right GUID string, and invokes the internal checker.

## Control Flow
The public checker optionally parses `ext_right` into a GUID, searches the target DN with `DSDB_FLAG_AS_SYSTEM | DSDB_SEARCH_SHOW_RECYCLED` to obtain security data, then delegates. The internal checker decodes the SD, gets `objectSid`, optionally inserts the GUID/access mask into an object tree, and calls `sec_access_check_ds()`. Failed checks log full debug context, set an LDB error string, and return `LDB_ERR_INSUFFICIENT_ACCESS_RIGHTS`.

## State and Persistence
The file does not mutate persistent state. It reads security descriptor and SID attributes from DSDB and allocates transient decoded structures on caller-provided talloc contexts.

## Dependencies and Integration Points
It depends on LDB, LDB modules/errors, NDR security decoding, Samba security token/descriptor checks, loadparm/auth types, SAMDB search utilities, and object-tree ACL helpers.

## Risks and Edge Cases
- Missing `nTSecurityDescriptor` is treated as insufficient access; malformed NDR becomes an operational error.
- The public search uses AS_SYSTEM intentionally; callers must ensure the checked `token` is the user/security context being authorized.
- Full security tokens/descriptors are logged at the requested debug level, which is useful but sensitive.

## Test Signals
Coverage should include allow and deny paths, missing/malformed SDs, invalid extended-right GUID strings, object-specific GUID checks, recycled object lookup, and error-string behavior. No direct test in this work item targets this file.
