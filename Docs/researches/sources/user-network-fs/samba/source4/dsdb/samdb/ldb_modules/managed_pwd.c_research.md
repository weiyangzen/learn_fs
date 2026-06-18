# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/managed_pwd.c

## Purpose
`managed_pwd.c` constructs the confidential `msDS-ManagedPassword` attribute for Group Managed Service Accounts. It is not a normal LDB module ops table; it exports `constructed_msds_managed_password()` for the constructed-attribute framework, which adds the packed managed-password blob to a search result when policy permits.

## Important APIs, types, and functions
The core helper is `gmsa_managed_password()`. It consumes an `ldb_context`, result message, parent request, and reply object. It uses GMSA helpers such as `dsdb_account_is_gmsa()`, `gmsa_allowed_to_view_managed_password()`, `dsdb_gmsa_current_time()`, `gmsa_recalculate_managed_pwd()`, and `gmsa_pack_managed_pwd()`. It may attach a `DSDB_CONTROL_GMSA_UPDATE_OID` reply control containing `struct gmsa_update`.

## Control flow
The function first checks `DSDB_OPAQUE_ENCRYPTED_CONNECTION_STATE_NAME`; if the connection is known to be unencrypted, it returns an operations error mapped to `WERR_DS_CONFIDENTIALITY_REQUIRED`. Non-GMSA accounts return success without adding the attribute. RODC operation is rejected because password construction must occur on a writable DC. For GMSA objects, the account SID is read, access is checked, and unauthorized callers receive success with no constructed value.

If allowed, the function obtains current DSDB GMSA time, recalculates the managed password, and asserts a new password is available. When recalculation says physical database keys/IDs should be refreshed, it adds a non-critical `DSDB_CONTROL_GMSA_UPDATE_OID` control to the reply and steals the update object into reply lifetime. Finally it packs new and optional previous password buffers plus query/unchanged intervals and adds `msDS-ManagedPassword` to the result message.

## State and persistence behavior
The constructed attribute is transient search-result state. Actual database refresh is signaled through the reply control rather than performed here. This keeps attribute construction side-effect-light while letting the LDAP server or surrounding framework persist GMSA password updates.

## Dependencies and integration points
This code integrates with DSDB GMSA utilities, LDAP encrypted-connection state, RODC detection, access-control checks for managed password viewing, NDR-generated GMSA structures, and constructed-attribute dispatch declared in `managed_pwd.h`.

## Risks and edge cases
Confidentiality and authorization failures must avoid leaking timing or partial password data. Unauthorized non-errors are intentional: the attribute is simply absent. RODC behavior is currently a hard failure with a TODO to forward to a writable DC. Errors while adding the update control are ignored, which preserves read behavior but may skip refresh signaling.

## Test signals
Test encrypted versus unencrypted LDAP, non-GMSA objects, writable DC versus RODC, allowed and denied readers, password packing with and without previous password, update-control attachment and ownership, and failure paths from SID extraction, time lookup, recalculation, and packing.
