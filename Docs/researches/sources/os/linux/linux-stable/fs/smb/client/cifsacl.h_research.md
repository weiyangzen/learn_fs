# File Research: sources/os/linux/linux-stable/fs/smb/client/cifsacl.h

Read status: complete.

## Purpose

Defines CIFS/SMB ACL constants and wire-format structures used by ACL parsing and construction code.

## Main Contents

- Permission bit constants:
  - `READ_BIT`
  - `WRITE_BIT`
  - `EXEC_BIT`
  - owner/group/everyone ACL masks
  - user/group bit shifts

- `DEFAULT_SEC_DESC_LEN`
  - Conservative default allocation size for a security descriptor with a DACL and several ACEs.

- `struct smb3_sd`
  - SMB3 self-relative security descriptor layout matching MS-DTYP/MS-SMB2 naming.
  - Contains revision, control flags, and owner/group/SACL/DACL offsets.

- ACL control flag definitions:
  - Self-relative, protected, inherited, present/defaulted, and resource-manager flags.

- `struct smb3_acl`
  - SMB3 ACL header layout with revision, size, and ACE count.

- `struct owner_sid`
  - Packed representation for special `S-1-5-88-*` Unix uid/gid/mode SIDs.

- `struct owner_group_sids`
  - Pair of owner and group special SIDs.

- Minimum length constants:
  - `MIN_SID_LEN`
  - `MIN_SEC_DESC_LEN`

## Dependencies

- Includes `../common/smbacl.h` for shared SID/ACL/security-descriptor definitions.

## Role in the Subsystem

This header supplies the ACL code with stable wire-format layouts and bounds constants. It is tightly coupled to `cifsacl.c` and to SMB2/SMB3 security descriptor handling.
