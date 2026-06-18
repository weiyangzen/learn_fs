# sources/user-network-fs/samba/source3/passdb/pdb_ldap.h

Purpose: declares the shared LDAP passdb private state and the small set of cross-file entry points exported by `pdb_ldap.c` to the wider passdb registration layer and to the NDS LDAP variant.

Important APIs/types/functions: `struct ldapsam_privates` holds `smbldap_state`, enumeration result/current entry/index state, domain name/SID, schema version, cached domain DN, NDS flag, LDAP server location, and a one-entry search cache for alias membership lookups. Function declarations expose `get_userattr_list`, `pdb_ldapsam_init_common`, `pdb_ldapsam_init`, `ldapsam_search_suffix_by_name`, and `priv2ld`. The header forward-uses LDAP types through included compilation context rather than declaring them itself.

Control flow: `pdb_ldap.c` allocates and owns `ldapsam_privates` during backend initialization. `pdb_nds.c` reuses the same private-data struct after calling `pdb_ldapsam_init_common`, then marks `is_nds_ldap`, stores `location`, and overrides selected callbacks. Search and enumeration methods mutate `result`, `entry`, and `index` fields; alias membership reverse search may populate `search_cache`.

State and persistence behavior: the header does not persist data directly, but its struct fields are the in-memory bridge to persistent LDAP state. `domain_dn` and `location` are heap strings freed by backend cleanup, `smbldap_state` owns the live LDAP connection, and `result`/`entry` point at LDAP message lifetimes that must be freed or transferred carefully.

Dependencies/integration: this header is coupled to Samba's `smbldap_state`, `dom_sid`, OpenLDAP `LDAPMessage`/`LDAP`, talloc allocation, passdb module registration, and the schema version constants from `pdb_ldap_schema.h`. It is the explicit ABI between base ldapsam and NDS ldapsam code.

Risks and test signals: duplicated declaration of `get_userattr_list` is harmless but noisy. The main risk is lifetime misuse of LDAP messages or cached search results stored in the private struct. Tests that iterate users/groups, interrupt paged searches, unload the backend, and exercise NDS initialization should reveal stale result or cleanup bugs.
