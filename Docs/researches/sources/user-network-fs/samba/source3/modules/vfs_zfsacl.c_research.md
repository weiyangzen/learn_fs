# sources/user-network-fs/samba/source3/modules/vfs_zfsacl.c

## Purpose
`vfs_zfsacl.c` converts between ZFS/Solaris NFSv4 ACLs and Samba NT ACLs. It provides NT ACL get/set support for ZFS or Solaris NFSv4 ACL filesystems and blocks conflicting POSIX draft ACL methods.

## Important APIs, Types, and Functions
`struct zfsacl_config_data` stores NFSv4 ACL conversion parameters and zfsacl options. `zfs_get_nt_acl_common()` converts an array of `ace_t` records to Samba `SMB4ACL_T`, maps special owner/group/everyone IDs, adds synchronize bits for allowed ACEs, handles directory delete-child behavior, optional inherited/protected DACL mapping, and special empty ACE blocking. `zfs_process_smbacl()` converts Samba SMB4 ACEs back to `ace_t` and writes them with `facl(ACE_SETACL)`. `zfsacl_fget_nt_acl()` reads with `facl(ACE_GETACLCNT/ACE_GETACL)`, converts to NT ACL, or falls back to a default protected ACL on unsupported filesystems. `zfsacl_fset_nt_acl()` calls `smb_set_nt_acl_nfs4()`.

## Control Flow
On connect, config reads `zfsacl:map_dacl_protected`, `zfsacl:denymissingspecial`, `zfsacl:block_special`, and common SMB ACL4 params. Get ACL reads native ACEs from a pathref fd, builds SMB4 ACLs, then lets shared NFSv4 conversion produce a security descriptor. Set ACL converts the incoming NT descriptor through shared NFSv4 helpers and a callback that writes the native ACE array.

## State and Persistence
The module stores per-share conversion flags only. Persistent ACL state is on the underlying ZFS/NFSv4 filesystem through `facl()`.

## Dependencies and Integration Points
It depends on `nfs4_acls.h`, `sunacl.h` when available, Solaris/ZFS `acl(2)` style `facl()`, Samba security descriptors, and NFSv4 ACL stat wrappers. It deliberately overrides POSIX ACL VFS methods with fail stubs to avoid incompatible Solaris ACL compatibility wrappers.

## Risks
ACL conversion is security-critical and depends on special ID handling. `zfsacl_denymissingspecial` can reject ACLs without owner/group/everyone mappings, while `zfsacl_block_special` inserts or filters zero-mask inherited everyone ACEs. Unsupported filesystem fallback creates a default protected ACL, which may surprise callers but avoids hard failure. Ordering relative to `vfs_solarisacl` matters.

## Test Signals
Tests should cover get/set of owner/group/everyone special ACEs, inherited DACL protected mapping, block-special filtering/insertion, deny-missing-special behavior, synchronize bit add/remove, directory add-file to delete-child mapping, unsupported `facl` fallback, and POSIX ACL method failure.
