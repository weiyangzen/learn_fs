# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_acl.c

Purpose: implements PVFS ACL backend registration, default ACL synthesis from Unix mode bits, ACL query/set operations, access checks, parent/create checks, inheritance, and maximal-access calculation.

Important APIs and functions: backend registry functions are `pvfs_acl_register`, `pvfs_acl_backend_byname`, and `pvfs_acl_init`. Security paths include `pvfs_default_acl`, `pvfs_acl_set`, `pvfs_acl_query`, `pvfs_access_check`, `pvfs_access_check_simple`, `pvfs_access_check_create`, `pvfs_access_check_parent`, `pvfs_acl_inherited_sd`, `pvfs_acl_inherit`, and `pvfs_access_maximal_allowed`. Helpers translate generic access bits, detect read-only shares, group membership, privileged owner access, and inheritable ACE behavior.

Control flow: query/set first try configured ACL ops, then fall back to default ACLs when no stored ACL exists. Set enforces `WRITE_OWNER`, `WRITE_DAC`, and `SYSTEM_SECURITY`, maps SIDs to Unix IDs for chown/fchown, optionally escalates with restore/take-ownership privileges, and saves only changed descriptors. Access checks reject write access on read-only shares, process delete-child from the parent, translate masks, load NT ACL xattrs where present, otherwise use Unix mode bits, and apply SMB1 read-attribute compatibility. Create checks validate parent rights, optionally build inherited security descriptors, and expand maximum allowed. Inheritance copies parent inheritable ACEs with creator-owner/group substitution and container/object flag rules.

State and persistence: registry is process-global. Stored ACL persistence is delegated to selected `pvfs_acl_ops` backends. Unix owner/group changes are persistent via chown. `name->allow_override` is set when permission override is allowed after NT ACL checks.

Dependencies and integration points: uses winbind ID mapping, Samba security descriptor helpers, security tokens/privileges, root privilege elevation, PVFS name resolution, xattr ACL load/save, and bracketing share flags.

Risks: this is security-critical. SID/XID mapping failures, privilege escalation handling, read-only enforcement, delete-child semantics, ACL fallback to Unix mode, and inheritance flag handling must match Windows expectations. Test signals include default ACL from modes, ACL set/query round trips, owner/group chown with and without privileges, NT ACL versus Unix fallback checks, SMB1/SMB2 access-mask differences, inheritance RAW-ACLS cases, and maximal-access results.
