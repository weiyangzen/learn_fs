# sources/user-network-fs/samba/source3/modules/vfs_solarisacl.h

## Purpose

`vfs_solarisacl.h` declares the Solaris ACL VFS module entry points used by Samba code and by `vfs_solarisacl.c`. It is a small prototype header for reading, writing, and deleting Solaris-backed ACLs through Samba's VFS ACL abstraction.

## Important APIs And Types

The header exposes `solarisacl_sys_acl_get_file()`, `solarisacl_sys_acl_get_fd()`, `solarisacl_sys_acl_set_fd()`, `solarisacl_sys_acl_delete_def_fd()`, and `vfs_solarisacl_init()`. These signatures use Samba types `vfs_handle_struct`, `files_struct`, `struct smb_filename`, `SMB_ACL_T`, `SMB_ACL_TYPE_T`, `TALLOC_CTX`, and `NTSTATUS`. It does not define any native Solaris ACL types; those are private to the C implementation.

## Control Flow And Integration

The intended flow is that VFS ACL hooks call the declared functions through the function table registered by `vfs_solarisacl_init()`. Callers pass a Samba filename or file descriptor wrapper plus an ACL type, and the implementation is responsible for conversion to/from Solaris ACL arrays. The header guard `__VFS_SOLARISACL_H__` protects repeated inclusion.

## State And Persistence

The header owns no state. It defines the module's external ABI within Samba and therefore constrains how other translation units can call Solaris ACL operations. Persistent ACL state remains in the filesystem.

## Dependencies

This header assumes that including translation units have already included Samba core type definitions for VFS handles, file structures, ACL types, talloc contexts, and NT status values. It is included by `vfs_solarisacl.c` after Samba base headers.

## Risks And Edge Cases

The declaration of `solarisacl_sys_acl_get_file()` is external, but the C file defines the function as `static`, creating an internal/external linkage mismatch. The header also makes the expected argument type explicit: callers must pass `const struct smb_filename *`, not a raw path string. That matters because the implementation reads `smb_fname->base_name`. Any mismatched caller can compile with warnings in permissive C modes but fail badly at runtime.

## Test Signals

Header-level validation is primarily compile coverage: include the header in the implementation and any platform-specific build that enables `vfs_solarisacl`, and build with warnings treated seriously. ABI tests should verify that the function table signatures match Samba's current VFS ACL hook typedefs.
