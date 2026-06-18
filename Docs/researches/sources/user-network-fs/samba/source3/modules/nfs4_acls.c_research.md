# sources/user-network-fs/samba/source3/modules/nfs4_acls.c

## Purpose
Core NFSv4 ACL conversion library. It converts between Samba's internal `SMB4ACL_T` list representation and Windows security descriptors, and supplies stat wrappers that retry with `CAP_DAC_OVERRIDE` for NFSv4 ACL protected paths.

## APIs, Types, And Control Flow
Private structs `SMB4ACE_T` and `SMB4ACL_T` store ACE properties, control flags, count, and a linked list. Exported helpers create ACLs, append and iterate ACEs, get/set control flags, identify inherited ACEs, read VFS parameters, wrap stat/fstat/lstat/fstatat, get NT ACLs from an SMB4 ACL, and set NT ACLs through a native setter callback. Read conversion maps NFSv4 special IDs (`OWNER@`, `GROUP@`, `EVERYONE@`) and uid/gid ACEs to SIDs, maps flags, optionally expands owner/group inheriting ACEs to creator-owner/group, suppresses inappropriate inheritance on files, and builds a security descriptor. Write conversion optionally changes owner/group, maps Windows ACEs to NFSv4 ACEs, resolves SIDs to Unix ids, handles duplicate ACE policy (`merge`, `ignore`, `reject`, `dontcare`), substitutes owner/group with special IDs in simple or special mode, copies descriptor control flags, and invokes the caller's native ACL writer as root when ownership changes require it.

## State, Dependencies, Integration
The ACL object is talloc-owned transient state. Persistent effects happen through the native `set_nfs4_native` callback and optional `chown_if_needed`. Dependencies include Samba id mapping, SID utilities, security descriptor builders, VFS stat calls, loadparm, and privilege elevation helpers. It is integrated by NFSv4 ACL VFS modules such as GPFS, ZFS, AIX ACL, and `vfs_nfs4acl_xattr`.

## Risks And Test Signals
Critical risks are authorization semantics drift when mapping inheritance, silent ACE drops when SIDs cannot map to Unix IDs, duplicate merge policy changing masks, root elevation around native set, owner/group substitution with `ID_TYPE_BOTH`, and deprecated modes still supported. Tests should cover round-trips between NFSv4 and NT ACLs, owner/group chown plus ACL write failure, file versus directory inheritance flags, duplicate ACE policies, unmappable SIDs, `SECINFO_*` combinations, `SEC_DESC_*` control flags, and EACCES stat fallback with and without capability.
