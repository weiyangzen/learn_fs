# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_acl_nfs4.c

Purpose: registers a PVFS ACL backend named `nfs4acl` that stores NT-style security descriptors in the `system.nfs4acl` NDR xattr format and translates between NFSv4 ACE IDs and Samba SIDs.

Important APIs and functions: `pvfs_acl_load_nfs4` reads `NFS4ACL_NDR_XATTR_NAME`, maps file owner/group and ACE UID/GID values to SIDs, and builds a `security_descriptor`. `pvfs_acl_save_nfs4` maps ACE trustee SIDs to Unix IDs and writes a `struct nfs4acl`. `pvfs_acl_nfs4_init` registers the backend with `pvfs_acl_register`. `ACE4_IDENTIFIER_GROUP` marks group principals.

Control flow: load allocates an NFS4 ACL object, calls `pvfs_xattr_ndr_load`, initializes an SD, prepares an `id_map` array for owner, group, and each ACE, calls `wbc_xids_to_sids`, assigns owner/group SIDs, and appends DACL ACEs. Save initializes NFS4 metadata from the SD, duplicates each trustee SID, calls `wbc_sids_to_xids`, fills ACE type/flags/mask/id, elevates with `root_privileges`, and writes with `pvfs_xattr_ndr_save`.

State and persistence: ACLs persist as NDR-encoded xattrs. Owner/group SIDs are reconstructed from current file `stat` UID/GID on load; ACEs persist their numeric IDs and group flag.

Dependencies and integration points: depends on PVFS xattr NDR helpers, generated NFS4 ACL NDR code, winbind ID mapping, security descriptor helpers, and root privilege elevation.

Risks: mapping failures block load/save; non-UID trustee mappings are saved as group ACEs; xattr write requires privilege; only DACL ACEs are represented. Test signals include load/save round trips, group ACE flag preservation, owner/group reconstruction, invalid or missing xattr handling, and permission failures on system xattrs.
