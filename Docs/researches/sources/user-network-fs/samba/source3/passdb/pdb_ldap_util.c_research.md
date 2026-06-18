# sources/user-network-fs/samba/source3/passdb/pdb_ldap_util.c

Purpose: contains domain-info bootstrap and lookup helpers for ldapsam. It searches for the `sambaDomain` object, creates it when requested, and initializes LDAP-backed account policy attributes with Samba defaults.

Important APIs/types/functions: private helpers are `add_new_domain_account_policies` and `add_new_domain_info`. The exported function is `smbldap_search_domain_info(struct smbldap_state *, LDAPMessage **, const char *domain_name, bool try_add)`.

Control flow: `smbldap_search_domain_info` escapes the domain name for an LDAP filter, searches under the configured suffix for exactly one `sambaDomain` object, and returns the LDAP result on success. If no entry exists and `try_add` is true, it calls `add_new_domain_info`, then `add_new_domain_account_policies`, and recursively searches again without adding. `add_new_domain_info` first checks for duplicate domain names, then builds an RDN-escaped DN, adds domain name, global SAM SID, algorithmic RID base, objectclass, and initial `sambaNextUserRid`. `add_new_domain_account_policies` iterates all account policy names, looks up default values, and writes each policy attribute as a replace mod on the domain DN.

State and persistence behavior: this file creates and mutates the LDAP `sambaDomain` object below `lp_ldap_suffix()`. It persists the domain SID from `get_global_sam_sid()`, the algorithmic RID base, legacy next-user RID seed, and account policy defaults. It allocates LDAP results for callers, who must free or talloc-autofree them.

Dependencies/integration: depends on `smbldap` search/add/modify wrappers, passdb account policy helpers, `lp_ldap_suffix`, schema maps from `pdb_ldap_schema.c`, SID formatting utilities, LDAP error APIs, and Samba memory helpers. `pdb_ldap.c` calls this during backend initialization and RID allocation.

Risks and test signals: duplicate `sambaDomain` entries are treated as fatal. Domain names are correctly escaped separately for filters and RDNs, which is important for special characters. Account policy initialization modifies one attribute at a time with a growing mod list, so failure partway through can leave a partially initialized domain object. Tests should cover no-entry creation, duplicate-entry rejection, special-character domain names, missing default policy retrieval, LDAP modify failures, and initialization idempotence.
