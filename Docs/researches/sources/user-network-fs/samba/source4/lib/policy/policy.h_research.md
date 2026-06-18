# sources/user-network-fs/samba/source4/lib/policy/policy.h

`policy.h` defines the source4 Group Policy C API. It declares link option bits, GPO disable flags, `enum gpo_inheritance`, and the core data structures `gp_context`, `gp_object`, `gp_link`, `gp_ini_param`, `gp_ini_section`, and `gp_ini_context`. It also prototypes LDAP, filesystem, INI, and management functions implemented across `gp_ldap.c`, `gp_filesys.c`, `gp_ini.c`, and `gp_manage.c`.

The central integration type is `gp_context`, which holds LDB, loadparm, credentials, tevent, cached SMB client state, and active DC information. `gp_object` represents both LDAP GPC metadata and the SYSVOL path. The API exposes direct mutation routines for LDAP links/inheritance/ACLs and filesystem GPT creation/push/ACL operations.

State ownership follows talloc conventions and is not encoded in the types, so callers must keep contexts and returned objects alive. Risks include broad header coupling to LDB/SMB/security types, lack of explicit transaction or consistency API, and callers misunderstanding which functions mutate LDAP, SYSVOL, or both. Test signals are compile coverage and integrated policy create/fetch/push/ACL tests.
