# sources/user-network-fs/samba/source3/passdb/pdb_ldap_schema.h

Purpose: defines Samba LDAP schema version constants, LDAP object class and common attribute names, integer attribute IDs, the `ATTRIB_MAP_ENTRY` structure, exported schema map arrays, and lookup helper prototypes.

Important APIs/types/functions: schema versions are `SCHEMAVER_SAMBAACCOUNT` and `SCHEMAVER_SAMBASAMACCOUNT`, with active code using the Samba 3.0 `sambaSamAccount` version. Object class constants cover account, group mapping, domain info, idmap/idpool, SID, trust password, trusted domain, POSIX account/group, and organizational unit classes. Attribute ID constants assign stable keys such as `LDAP_ATTR_UID`, `LDAP_ATTR_USER_SID`, `LDAP_ATTR_GROUP_TYPE`, `LDAP_ATTR_NEXT_RID`, `LDAP_ATTR_PWD_HISTORY`, and `LDAP_ATTR_LOGON_HOURS`. The public helpers are `get_attr_key2string` and `get_attr_list`.

Control flow: implementation files use integer IDs rather than hard-coded strings for most schema lookups. `pdb_ldap.c` wraps user-specific calls through schema-version dispatch, while domain/group/account-policy code accesses the exported maps directly.

State and persistence behavior: this header is declarative, but it defines the symbolic vocabulary for all LDAP persistence in this backend. The same constants are used to build filters, LDAP mods, and deletion requests, so a mismatch between constants and deployed LDAP schema affects runtime data layout.

Dependencies/integration: integrates with talloc through helper prototypes and with all LDAP passdb files through shared objectclass/attribute constants. It also bridges Samba passdb concepts, POSIX account/group objects, and idmap/trust object classes.

Risks and test signals: `LDAP_ATTR_USER_SID` and `LDAP_ATTR_USER_RID` intentionally share value 18 for old/new schema compatibility, which is easy to misread. Any new schema field requires coordinated table updates in `pdb_ldap_schema.c`. Compile tests catch missing declarations, but integration tests against an LDAP server are needed to catch wrong schema names.
