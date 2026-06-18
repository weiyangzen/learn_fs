# sources/user-network-fs/samba/source3/winbindd/idmap_ldap.c

## Purpose
This backend stores SID-to-Unix-ID mappings and allocation state in LDAP. It supports allocating new UID/GID values from a `sambaUnixIdPool` entry and creating `sambaIdmapEntry`/SID objects under a configured suffix. It is online-only and refuses operations when `idmap_is_offline()` is true.

## Important APIs, Types, And Functions
`struct idmap_ldap_context` holds `smbldap_state`, URL, suffix, bind DN, anonymous flag, and `idmap_rw_ops`. Initialization is `idmap_ldap_db_init`; allocation is `idmap_ldap_allocate_id_internal` and default-domain wrapper `idmap_ldap_allocate_id`; persistence is `idmap_ldap_set_mapping`; mapping is `idmap_ldap_unixids_to_sids` and `idmap_ldap_sids_to_unixids`; `idmap_ldap_init` registers the backend. Credential setup is in `get_credentials`, and pool verification/creation is in `verify_idpool`.

## Control Flow
Initialization reads `ldap_url` and `ldap_base_dn` or the global LDAP idmap suffix, initializes an smbldap connection, fetches credentials from `idmap config <domain> : ldap_user_dn` secret storage or legacy LDAP password storage, sets a destructor, and verifies the id pool. Allocation searches for the single idpool object, reads `uidNumber` or `gidNumber`, range-checks it, then atomically modifies LDAP by deleting the old attribute value and adding the incremented value. Mapping lookups build one LDAP filter for a single map or batched OR filters up to `IDMAP_LDAP_MAX_IDS`, parse returned SID/uidNumber/gidNumber attributes, match them back to requested maps, and mark unmapped entries. SID-to-ID additionally attempts `idmap_rw_new_mapping` for unmapped SIDs.

## State And Persistence
Persistent state lives in LDAP: pool counters under `sambaUnixIdPool` and mapping entries named by SID under the suffix. New mappings are not wrapped in a multi-operation LDAP transaction, so allocation and entry creation can diverge on failure. The context holds one smbldap connection and is freed by destructor.

## Dependencies And Integration
The file depends on OpenLDAP APIs, Samba `smbldap`, passdb LDAP schema names, secrets, global tevent context, `idmap_rw`, and idmap utility lookup helpers. It integrates with the idmap allocator contract and Samba configuration.

## Risks And Test Signals
Test offline behavior, missing URL/suffix, anonymous and authenticated binds, missing/multiple idpool entries, allocation at high_id, malformed numeric attributes, duplicate LDAP entries, batched filters, and unmapped SID allocation requiring type hints. The allocation operation is only as atomic as the LDAP modify on a single pool entry; mapping creation can leave consumed IDs without entries. LDAP filters include stringified SIDs and numeric IDs; escaping and schema assumptions should be validated.
