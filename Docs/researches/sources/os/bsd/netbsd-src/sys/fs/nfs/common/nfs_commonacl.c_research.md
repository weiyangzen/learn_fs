# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_commonacl.c

## Purpose
Implements common NFSv4 ACL encode/decode, permission-mask translation, ACL setting, and ACL comparison helpers shared by NFS client/server code.

## Main Interfaces
- `nfsrv_dissectace` decodes one NFSv4 ACE from XDR into a kernel `acl_entry`, resolving special principals and named users/groups.
- `nfsrv_buildacl` serializes a kernel NFSv4 ACL to XDR ACEs and writes the entry count.
- `nfsrv_setacl` validates ACL support and size constraints, then calls `VOP_SETACL`.
- `nfsrv_compareacl` compares two ACLs for count, tag/id, and permission equality.
- Static `nfsrv_acemasktoperm` maps NFSv4 ACE mask bits to kernel ACL permission bits.

## Decode Behavior
- Handles special principals `OWNER@`, `GROUP@`, and `EVERYONE@`.
- Uses `nfsv4_strtouid`/`nfsv4_strtogid` for named user/group principals.
- Converts NFSv4 flags to `ACL_ENTRY_*` inheritance/audit flags.
- Converts allow/deny/audit/alarm ACE types to kernel entry types.
- Rejects unsupported flag or mask bits with `NFSERR_ATTRNOTSUPP`.
- Treats zero-length who strings from some NetApp filers as an undefined deny entry.

## Encode Behavior
- Converts kernel ACL tags back to special strings or user/group name strings using `nfsv4_uidtostr`/`nfsv4_gidtostr`.
- Maps directory permissions to `LISTDIRECTORY`, `ADDFILE`, `ADDSUBDIRECTORY`, `SEARCH`, etc., and non-directory permissions to `READDATA`, `WRITEDATA`, `APPENDDATA`, `EXECUTE`, etc.
- Preserves supported inheritance/audit flags and group identifier flag.

## Dependencies
Depends on NFS XDR macros, NFSv4 ACL constants, kernel ACL types, uid/gid string mapping helpers, `nfs_supportsnfsv4acls`, and `VOP_SETACL`.

## Risks
- Directory and regular-file permission masks differ; using the wrong vnode type when building ACEs changes wire semantics.
- Name-string conversion can allocate dynamically; callers rely on correct free behavior for returned buffers.
- `nfsrv_compareacl` compares only selected fields and does not consider all possible ACE metadata such as entry type/flags in every case.
