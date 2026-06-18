# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_xattr.c

Purpose: `pvfs_xattr.c` is the persistence layer for PVFS DOS metadata, EAs, streams, and NT ACLs. It abstracts system xattrs and the optional TDB-backed EADB, and serializes Samba xattr structures with NDR.

Important APIs, types, and functions: Public functions include `pvfs_xattr_unlink_hook`, `pvfs_xattr_ndr_load`, `pvfs_xattr_ndr_save`, `pvfs_dosattrib_load/save`, `pvfs_doseas_load/save`, `pvfs_streams_load/save`, `pvfs_acl_load/save`, `pvfs_xattr_create/delete/load/save`, and `pvfs_xattr_probe`. Internal helpers are `pull_xattr_blob`, `push_xattr_blob`, and `delete_xattr`.

Control flow: Blob operations dispatch to EADB helpers when `pvfs->ea_db` is configured, otherwise to system xattr helpers. Unsupported system xattrs clear `PVFS_FLAG_XATTR_ENABLE` and are treated as not found. NDR load/save wrappers pull or push blobs around generated xattr structures. DOS attribute load initializes stream existence, reads versioned `xattr_DosAttrib`, normalizes attributes, restores EA size/allocation/create/change fields, then refreshes stream info. Save writes version 1. EA, stream-index, and ACL load/save functions map missing xattrs to empty state where appropriate. ACL save temporarily gains root privileges for the system namespace. Probe attempts user and security namespace reads to disable unsupported xattrs early.

State and persistence behavior: This file is responsible for durable metadata outside normal POSIX stat data. It stores DOS attributes, DOS EAs, stream indexes, stream payload xattrs via generic helpers, and NT ACL descriptors either in filesystem xattrs or a TDB EADB. Unlink hooks remove backend metadata.

Dependencies and integration points: It depends on NDR-generated xattr types, posix_eadb backend functions, system xattr backend functions, root privilege helpers, allocation/attribute normalization, and is used by open, resolve, query/set info, streams, unlink, and ACL code.

Risks: Disabling xattrs after one unsupported error changes later metadata behavior for the share. Versioned DOS attribute parsing must remain backward-compatible. System ACL xattrs require privilege handling. EADB and system xattr backends must remain behaviorally equivalent. Missing stream indexes can orphan stream payload xattrs.

Test signals: Cover xattr unsupported fallback, EADB and system backends, DOS attribute version 1 and old version 2 loads, DOS EA empty/missing behavior, stream index persistence, ACL save/load with privileges, unlink cleanup, and probe behavior.
