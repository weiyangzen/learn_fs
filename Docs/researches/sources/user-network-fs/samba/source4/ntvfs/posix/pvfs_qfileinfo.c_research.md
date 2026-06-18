# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_qfileinfo.c

Purpose: `pvfs_qfileinfo.c` implements path and handle metadata queries for the POSIX NTVFS backend. It maps `struct pvfs_filename` stat/DOS/xattr/ACL/stream state into the many SMB1, trans2, NT, and SMB2 file-information levels.

Important APIs, types, and functions: Public functions are `pvfs_query_ea_list`, `pvfs_qpathinfo`, and `pvfs_qfileinfo`. Important helpers are `pvfs_fileinfo_access`, `pvfs_query_all_eas`, and `pvfs_map_fileinfo`. It fills `union smb_fileinfo`, `struct smb_ea_list`, `struct stream_information`, and security descriptor query structures.

Control flow: `pvfs_qpathinfo` resolves the input path with stream support, verifies the stream exists, checks open-db stat permission through `pvfs_can_stat`, enforces the access bits required by the information level, then calls `pvfs_map_fileinfo`. `pvfs_qfileinfo` finds the open handle, checks the handle's granted access mask, refreshes the handle name and DOS metadata through `pvfs_resolve_name_handle`, maps common fields, then patches handle-only fields such as delete-pending, current position, access mask, and mode.

State and persistence behavior: This file does not mutate filesystem data. It reads current POSIX stat data, DOS metadata stored in xattrs/EADB, stream indexes, EA lists, ACL xattrs, open-db delete-on-close/write-time state, and handle-local position/mode fields. For SMB2 all-information, it synthesizes a share-prefixed path rather than exposing the real server path.

Dependencies and integration points: It depends on `pvfs_resolve.c`, access checks, `pvfs_open.c` share/stat helpers, xattr EA loaders, stream information helpers, ACL query hooks, short-name mangling, and protocol version checks.

Risks: Each information level has slightly different access and field semantics; regressions here are often wire-compatibility regressions. `name_info` is deliberately unsupported for SMB2 in one level. Delete-pending decrements link count in handle queries only. EA queries omit zero-length EAs and SMB2 all-EAs maps no EAs to `NT_STATUS_NO_EAS_ON_FILE`.

Test signals: Cover every `RAW_FILEINFO_*` level, especially SMB2 all information, stream info, all-EAs/no-EAs behavior, security descriptors with SACL flags, delete-on-close visibility, handle position/mode reporting, and path queries blocked by share-mode or ACL rules.
