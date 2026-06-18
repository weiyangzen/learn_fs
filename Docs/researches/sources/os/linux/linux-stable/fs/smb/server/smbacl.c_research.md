# File Research: sources/os/linux/linux-stable/fs/smb/server/smbacl.c

## Summary
Implements conversion between SMB/NT security descriptors and Linux ownership, mode bits, POSIX ACLs, and ksmbd xattr-backed Windows ACL behavior. It handles SID construction/comparison, NT DACL parsing/building, ACL inheritance, permission checks, and applying security-info updates to filesystem objects.

## Main Responsibilities
- Define well-known SIDs used by ksmbd: domain SID template, creator owner/group, Everyone, Authenticated Users, Unix user/group SIDs, and NFS-style Unix uid/gid/mode SIDs.
- Compare and copy SMB SIDs and map uid/gid values to SIDs or SIDs back to kernel ids with idmapped-mount support.
- Convert ACE access masks into POSIX mode bits and POSIX mode/ACL entries back into SMB ACE access masks.
- Parse incoming security descriptors, validate owner/group/DACL offsets and SID/ACE bounds, and fill `struct smb_fattr`.
- Build self-relative NT security descriptors from current inode metadata, POSIX ACLs, and optionally a previous NT descriptor.
- Preserve inherited or existing NT ACEs while adding POSIX ACL-derived ACEs.
- Inherit DACLs from parent NTACL xattrs, including creator-owner/group substitution and inheritance flag handling.
- Check requested SMB access against stored Windows ACL xattrs and fallback POSIX ACL entries.
- Apply `SET_INFO` security changes: update uid/gid/mode, replace POSIX ACL xattrs, and store NTACL xattrs when configured.
- Initialize ksmbd’s configured domain SID.

## Key Interfaces
- Conversion: `parse_sec_desc()`, `build_sec_desc()`, `smb_acl_sec_desc_scratch_len()`.
- ACL state helpers: `init_acl_state()`, `free_acl_state()`, `posix_state_to_acl()`.
- SID helpers: `compare_sids()`, `id_to_sid()`, `ksmbd_init_domain()`.
- Inheritance/access: `smb_inherit_flags()`, `smb_inherit_dacl()`, `smb_check_perm_dacl()`, `set_info_sec()`.

## Important Behavior
`parse_sec_desc()` accepts self-relative NT security descriptors, validates offsets against the supplied buffer length, maps owner/group SIDs through the mount idmap, preserves DACL control flags, and delegates ACE parsing to `parse_dacl()`.

`build_sec_desc()` constructs owner, group, and DACL sections according to requested security-info bits. Without a previous descriptor it derives a DACL from mode/POSIX ACLs; with one it copies valid existing ACEs and appends POSIX ACL-derived entries.

Inheritance reads the parent `security.NTACL` xattr, validates parent SID and DACL bounds, filters ACEs by object/container inheritance flags, substitutes creator owner/group with the new child uid/gid, and stores a new NTACL xattr on the child.

Permission checking prefers NTACL xattrs, computes maximal access when requested, searches matching user/NFS-mode/Everyone ACEs, consults POSIX ACLs for named user/group fallback, and rejects access when requested bits exceed allowed bits plus always-permitted metadata rights.

## Cross-File Interactions
Uses `smb_map_generic_desired_access()` from `smb_common.c`, xattr helpers from `vfs.c`, xattr formats from `xattr.h`, share flags from management config, and common SMB ACL wire types from `../common/smbacl.h`. Called by SMB2 create/query/set security paths and VFS ACL initialization/inheritance paths.

## Risks
This file parses attacker-controlled security descriptors and xattr-backed ACL blobs. Bounds checks around offsets, ACE sizes, SID subauthority counts, inherited ACE allocation, and descriptor size arithmetic are critical. Semantics are also subtle: small changes can break Windows ACL compatibility, POSIX ACL preservation, idmapped mount ownership, or durable Samba/ksmbd xattr interoperability.
