<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_acl_common.c -->
# sources/user-network-fs/samba/source3/modules/vfs_acl_common.c

## Purpose
This file provides common logic for VFS modules that persist Windows NT security descriptors outside the native filesystem ACL path, primarily `acl_xattr` and `acl_tdb`. It serializes/deserializes NT ACL blobs, validates them against underlying filesystem ACL hashes, merges incoming partial security descriptor updates, and supplies shared delete/chmod behavior.

## Important APIs, Types, And Functions
Public functions are `init_acl_common_config`, `fget_nt_acl_common`, `fset_nt_acl_common`, `rmdir_acl_common`, `unlink_acl_common`, and `fchmod_acl_module_common`. Internal functions include `parse_acl_blob`, `create_acl_blob`, `create_sys_acl_blob`, `hash_blob_sha256`, `hash_sd_sha256`, `validate_nt_acl_blob`, `add_directory_inheritable_components`, `set_underlying_acl`, `store_v3_blob`, and `acl_common_remove_object`.

## Control Flow
`init_acl_common_config` reads module parameters `ignore system acls` and `default acl style` into handle data. Get flow fetches a backend blob, parses xattr NTACL versions 1-4, validates version 3/4 hashes unless system ACLs are ignored, falls back to the lower VFS NT ACL when needed, synthesizes default ACLs when ignoring system ACLs, adds inheritable directory components if the filesystem ACL lacks them, strips protected-DACL bits, and filters owner/group/DACL/SACL according to `security_info`. Set flow first fetches the current full descriptor, overlays incoming owner/group/DACL/SACL portions, rejects macOS MS-NFS chmod descriptors, marks the fsp extension as `setting_nt_acl`, optionally sets only ownership in the lower layer when system ACLs are ignored, otherwise sets the lower ACL, hashes the resulting lower NT ACL and optional sys-ACL blob, then stores a version 3 or 4 serialized descriptor via the backend callback.

## State And Persistence
Per-share config is stored on the VFS handle. A transient `acl_common_fsp_ext` flag prevents lower-layer POSIX ACL changes made during NT ACL setting from deleting the stored NT ACL. Durable persistence is delegated to backend callbacks; this file defines the NDR blob shape and SHA-256 hash validation. Delete helpers may temporarily become root to remove files opened with delete-on-close and `DELETE_ACCESS`.

## Dependencies And Integration Points
The file depends on Samba security descriptor/NDR code, `librpc/gen_ndr/ndr_xattr.h`, passdb SID lookup, gnutls SHA-256 hashing, VFS lower-layer ACL calls, xattr/sys-ACL blob hooks, talloc, loadparm, and SMB file-open tracking. It is the integration spine for `vfs_acl_tdb.c` and `vfs_acl_xattr.c`.

## Risks
Hash validation must stay compatible with older xattr versions while detecting underlying ACL drift. Version 3 validation only hashes the lower NT descriptor, while version 4 also hashes the system ACL blob when available. The root override path for owner changes and delete-on-close must preserve Windows semantics without granting arbitrary chown/delete. `ignore system acls` changes create masks and makes stored descriptors authoritative, so configuration mistakes can hide filesystem ACL changes.

## Test Signals
Important tests cover xattr/TDB get/set with versions 1-4, hash match/mismatch fallback, system ACL blob unavailable, `ignore system acls`, directory inheritable ACE synthesis, MS-NFS chmod ignore, owner take-over with `SEC_STD_WRITE_OWNER`, delete-on-close root override, and POSIX-open-only chmod pass-through.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_acl_common.c -->
