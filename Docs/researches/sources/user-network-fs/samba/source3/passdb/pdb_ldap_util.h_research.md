# sources/user-network-fs/samba/source3/passdb/pdb_ldap_util.h

Purpose: declares the LDAP domain-info search/bootstrap helper used by ldapsam, behind `HAVE_LDAP`.

Important APIs/types/functions: the sole exported prototype is `smbldap_search_domain_info`, which accepts an `smbldap_state`, output `LDAPMessage **`, domain name, and `try_add` flag, returning an `NTSTATUS`.

Control flow: callers include this header when they need to resolve or create the `sambaDomain` LDAP entry. `pdb_ldap.c` uses it during initialization and RID allocation; `pdb_ldap_util.c` owns implementation details.

State and persistence behavior: the header has no state, but the function contract returns an LDAP message result that callers must manage and may create persistent LDAP domain metadata if `try_add` is true.

Dependencies/integration: guarded by `HAVE_LDAP`, and depends on Samba `NTSTATUS`, `smbldap_state`, and OpenLDAP `LDAPMessage` types from surrounding includes.

Risks and test signals: consumers must not assume the output result is valid on failure, and must free it on success. Build coverage should include both LDAP-enabled and LDAP-disabled configurations; runtime coverage should verify initialization behavior through `pdb_ldapsam_init_common`.
