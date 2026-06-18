<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_aixacl_util.c -->
# sources/user-network-fs/samba/source3/modules/vfs_aixacl_util.c

## Purpose
This utility converts between AIX classic ACL structures and Samba's `SMB_ACL_T` representation. It is shared by the classic AIX ACL module and the JFS2/AIXC fallback paths.

## Important APIs, Types, And Functions
Exported functions are `aixacl_to_smbacl` and `aixacl_smb_to_aixacl`. Internal helper `aixacl_smb_to_aixperm` maps `SMB_ACL_READ`, `SMB_ACL_WRITE`, and `SMB_ACL_EXECUTE` to AIX `R_ACC`, `W_ACC`, and `X_ACC`.

## Control Flow
`aixacl_to_smbacl` initializes a Samba ACL, walks extended AIX ACL entries when `S_IXACL` is enabled, skips entries with unsupported multi-id forms, maps `ACEID_USER` and `ACEID_GROUP` to named user/group ACL entries, converts `ACC_PERMIT`/`ACC_SPECIFY` directly, approximates `ACC_DENY` by inverting low permission bits, then appends synthetic owner, group-object, and other entries from `u_access`, `g_access`, and `o_access`. `aixacl_smb_to_aixacl` allocates a variable-length AIX ACL, fills base owner/group/other permissions from object entries, skips masks, and appends named user/group `ACC_SPECIFY` entries with one `ace_id`.

## State And Persistence
The utility has no durable state. It allocates returned AIX ACLs with `SMB_MALLOC` for callers to free and returned Samba ACL entries under the provided talloc context.

## Dependencies And Integration Points
Dependencies include AIX `struct acl`, `struct acl_entry`, `struct ace_id` layout macros, Samba ACL compatibility types, talloc, and Samba allocation/debug helpers. It is used by `vfs_aixacl.c` and `vfs_aixacl2.c`.

## Risks
DENY ACLs are lossy because Samba's POSIX ACL abstraction cannot represent deny entries; the code inverts permissions to approximate a permit mask. Multi-identifier AIX entries are skipped. There is a suspicious check after `talloc_realloc` in the extended-entry loop that tests `result == NULL` rather than `result->acl == NULL`, which could miss allocation failure. Buffer growth for AIX ACL construction must keep `acl_len` and allocation size synchronized.

## Test Signals
Tests should round-trip base owner/group/other entries, named user/group entries, deny approximation, disabled `S_IXACL`, mask skipping, dynamic ACL buffer growth, unsupported multi-id entries, and allocation-failure paths where possible.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_aixacl_util.c -->
