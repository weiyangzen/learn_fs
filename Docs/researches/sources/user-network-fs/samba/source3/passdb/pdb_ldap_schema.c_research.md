# sources/user-network-fs/samba/source3/passdb/pdb_ldap_schema.c

Purpose: provides the LDAP schema attribute maps used by ldapsam to convert logical passdb fields into concrete LDAP attribute names for users, domain info, group mappings, id pools, SID maps, and trusted password objects.

Important APIs/types/functions: exported tables include `attrib_map_v30`, `attrib_map_to_delete_v30`, `dominfo_attr_list`, `groupmap_attr_list`, `groupmap_attr_list_to_delete`, `idpool_attr_list`, and `sidmap_attr_list`. `get_attr_key2string` performs integer-key lookup in an `ATTRIB_MAP_ENTRY` array. `get_attr_list` allocates a NULL-terminated talloc array of attribute names for LDAP search requests.

Control flow: callers pass one of the mapping arrays and either request a single attribute name by key or a whole search attribute list. Tables are terminated by `LDAP_ATTR_LIST_END`. User schema v30 maps `sambaSamAccount` fields such as `sambaSID`, `sambaNTPassword`, `sambaLMPassword`, `sambaAcctFlags`, password history, lockout counters, profile paths, and logon hours. Delete tables omit structural/POSIX fields so `ldapsam_delete_entry` can strip Samba-specific attributes without necessarily deleting the entire object.

State and persistence behavior: this file has only static mapping data; persistence effects occur in callers that use the returned names to read or write LDAP. The map contents define the durable LDAP attribute contract, so changes here are schema migrations in practice.

Dependencies/integration: depends on `pdb_ldap_schema.h` constants and Samba talloc/debug helpers. The maps are consumed throughout `pdb_ldap.c` and `pdb_ldap_util.c` for filters, add/modify lists, deletion lists, and account policy/domain metadata access.

Risks and test signals: incorrect attribute names silently break lookup, add, or deletion paths against live LDAP schemas. The delete-list tables are especially sensitive because including an RDN or shared idmap attribute can trigger LDAP naming/objectclass violations. Tests should verify generated search attribute lists, user add/update/delete against Samba schema, group mapping delete fallback behavior, and domain-info bootstrap.
