# File Research: sources/os/linux/linux/fs/smb/client/cifsacl.h

## Purpose
`cifsacl.h` defines CIFS/SMB security descriptor and ACL constants used by ACL translation code.

## Main Contents
- Includes shared SMB ACL wire structures from `../common/smbacl.h`.
- Defines POSIX permission masks and bit shifts:
  - `READ_BIT`, `WRITE_BIT`, `EXEC_BIT`
  - `ACL_OWNER_MASK`, `ACL_GROUP_MASK`, `ACL_EVERYONE_MASK`
  - `UBITSHIFT`, `GBITSHIFT`
- Defines `DEFAULT_SEC_DESC_LEN`, the minimum allocation target for a security descriptor containing owner, group, and several ACEs.
- Defines SMB3 security descriptor structure `struct smb3_sd`.
- Defines SMB3 ACL header `struct smb3_acl`.
- Defines special owner/group SID structures used for NFS-style persisted uid/gid:
  - `struct owner_sid`
  - `struct owner_group_sids`
- Defines minimum SID/security descriptor lengths:
  - `MIN_SID_LEN`
  - `MIN_SEC_DESC_LEN`

## Security Descriptor Flags
The file enumerates `ACL_CONTROL_*` flags matching MS-DTYP self-relative security descriptor control bits, including DACL/SACL present/defaulted/protected/inherited flags and resource-manager/self-relative flags.

## Role in the Group
This header is the local schema companion for `cifsacl.c`. It does not implement logic; it supplies wire-format structures and constants needed to parse and synthesize ACL/security-descriptor blobs.
