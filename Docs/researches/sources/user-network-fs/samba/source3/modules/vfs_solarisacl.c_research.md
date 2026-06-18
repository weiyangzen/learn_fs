# sources/user-network-fs/samba/source3/modules/vfs_solarisacl.c

## Purpose

`vfs_solarisacl.c` implements Samba VFS POSIX ACL hooks for Solaris-style ACL storage. It translates between Samba's internal `SMB_ACL_T` model and Solaris `aclent_t` arrays, then uses Solaris `acl()`, `facl()`, and `aclsort()` to read, write, and delete default ACL state. The module registers as `solarisacl` and is intended to sit in the VFS stack where Samba needs Solaris-native ACL semantics rather than the generic POSIX ACL backend.

## Important APIs, Types, And Functions

The file aliases Solaris ACL concepts with `SOLARIS_ACE_T`, `SOLARIS_ACL_T`, `SOLARIS_ACL_TAG_T`, and `SOLARIS_PERM_T`, all backed by Solaris `aclent_t`/mode types. `_IS_DEFAULT()` detects `ACL_DEFAULT`; `_IS_OF_TYPE()` filters access versus default entries for Samba's `SMB_ACL_TYPE_ACCESS` and `SMB_ACL_TYPE_DEFAULT`.

Public VFS-facing functions are `solarisacl_sys_acl_get_fd()`, `solarisacl_sys_acl_set_fd()`, and `solarisacl_sys_acl_delete_def_fd()`, with `solarisacl_sys_acl_get_file()` implemented as an internal helper despite being declared in the companion header. Private conversion helpers include `smb_acl_to_solaris_acl()`, `solaris_acl_to_smb_acl()`, `smb_tag_to_solaris_tag()`, `solaris_tag_to_smb_tag()`, `solaris_perm_to_smb_perm()`, and `smb_perm_to_solaris_perm()`. System-call helpers `solaris_acl_get_file()`, `solaris_acl_get_fd()`, `solaris_add_to_acl()`, and `solaris_acl_sort()` allocate and normalize the native ACL arrays.

The VFS table binds `sys_acl_get_fd_fn`, `sys_acl_blob_get_fd_fn`, `sys_acl_set_fd_fn`, and `sys_acl_delete_def_fd_fn`; `vfs_solarisacl_init()` registers the module with `smb_register_vfs()`.

## Control Flow

ACL reads call `facl(fd, GETACLCNT)` or `acl(path, GETACLCNT)`, allocate an `aclent_t` array of the returned size, fetch entries with `GETACL`, and convert only entries matching the requested access/default type. Conversion builds a Samba ACL by appending `struct smb_acl_entry` values and mapping Solaris tags such as `USER_OBJ`, `GROUP_OBJ`, `OTHER_OBJ`, and `CLASS_OBJ` to Samba tags.

ACL writes start from the caller-supplied Samba ACL, convert it to a Solaris ACL of the requested type, fetch the other ACL half from the file descriptor, append that other half, sort/validate with `aclsort()`, and submit the combined array with `facl(fd, SETACL, count, solaris_acl)`. Default ACL deletion is implemented by reading only the access ACL and writing it back with `acl(path, SETACL)`, relying on Solaris behavior that a directory `SETACL` replaces both access and default entries with the provided set.

## State And Persistence

The module has no durable module-private storage. Persistent state is entirely the filesystem ACL stored by Solaris. Temporary ACL arrays are heap allocated with Samba allocation helpers and freed at function exit. `errno` is used as the primary failure channel for VFS operations returning Unix-style errors.

## Dependencies And Integration Points

The module depends on Samba VFS headers, `files_struct`, `smb_filename`, talloc-backed ACL helpers, and Solaris ACL APIs from `system/filesys.h`. Build integration appears in `source3/modules/wscript_build` as `vfs_solarisacl`, and `source3/wscript` can add it to required static modules on Solaris-like builds. It also delegates ACL blob serialization to `posix_sys_acl_blob_get_fd`.

## Risks And Edge Cases

The source has high-risk implementation defects: `solarisacl_sys_acl_get_file()` is declared non-static in the header but defined static in the C file, and `solarisacl_sys_acl_delete_def_fd()` passes `fsp->fsp_name->base_name` to a function that expects `const struct smb_filename *`, which would dereference a string pointer as a structure. There is also a `DBG_DEBG` typo in an error path. These look like compile or runtime blockers unless hidden by version-specific macro behavior outside this file. Functional risks include relying on callers to supply mask entries, using `aclsort()` as the main validity gate, and preserving the unrelated access/default half by refetching it immediately before write, which can race with other ACL writers.

## Test Signals

Useful tests should cover access and default ACL round trips, deletion of a directory default ACL while preserving access entries, invalid ACL type rejection, invalid tag handling, and Solaris-specific mask normalization. Build tests are especially important for this snapshot because of the apparent prototype, argument, and debug macro inconsistencies. Runtime tests need a filesystem and platform that provide Solaris `acl()`, `facl()`, `aclent_t`, and `aclsort()`.
