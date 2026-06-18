<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_acl_common.h -->
# sources/user-network-fs/samba/source3/modules/vfs_acl_common.h

## Purpose
This header declares the shared contract used by Windows-ACL persistence modules such as `acl_xattr` and `acl_tdb`. It exposes common configuration, fsp extension state, and helper functions for get/set/delete/chmod behavior.

## Important APIs, Types, And Functions
`struct acl_common_config` holds `ignore_system_acls`, `default_acl_style`, and an optional `security_acl_xattr_name`. `struct acl_common_fsp_ext` carries the `setting_nt_acl` guard. Function declarations include `init_acl_common_config`, `rmdir_acl_common`, `unlink_acl_common`, `fchmod_acl_module_common`, `chmod_acl_acl_module_common`, `get_nt_acl_common_at`, `fget_nt_acl_common`, and `fset_nt_acl_common`. The get/set common functions are callback-driven so each backend supplies blob fetch/store functions.

## Control Flow
The header has no execution flow. Its function-pointer signatures define how backend modules hand storage operations to the common ACL engine while the common engine handles security descriptor merging and validation.

## State And Persistence
The structs define per-handle configuration and per-open-file transient state. Durable persistence is not specified here; it is supplied by backend modules through callbacks.

## Dependencies And Integration Points
The header includes `smbd/proto.h` and relies on Samba VFS, `files_struct`, `smb_filename`, `DATA_BLOB`, `security_descriptor`, and `NTSTATUS` types. It is included by ACL storage modules and any code sharing the common delete/chmod logic.

## Risks
The header declares `chmod_acl_acl_module_common` and `get_nt_acl_common_at`, but this source batch did not include implementations for them; consumers must only use APIs available in the linked build. Backend callbacks must obey ownership expectations for returned `DATA_BLOB` buffers.

## Test Signals
Compile/link tests of `acl_xattr` and `acl_tdb` validate this contract. Runtime signals come from backend get/set tests that exercise the callback signatures and `acl_common_fsp_ext` guard.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_acl_common.h -->
