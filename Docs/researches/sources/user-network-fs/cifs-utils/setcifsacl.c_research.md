# sources/user-network-fs/cifs-utils/setcifsacl.c

## Purpose
`setcifsacl.c` implements the `setcifsacl` command, a CIFS/SMB userspace helper that edits NT security descriptors exposed by the Linux CIFS client through extended attributes. It can add, add-and-reorder, delete, modify, or replace DACL/SACL ACEs, and can replace owner or group SIDs. It is intentionally descriptor-component scoped: it modifies one component and preserves the rest.

## Important APIs, types, and functions
The code depends on `cifsacl.h` descriptor structures such as `struct cifs_ntsd`, `struct cifs_ctrl_acl`, `struct cifs_ace`, and `struct cifs_sid`, plus `ace_kinds`. It uses `getxattr`/`setxattr` against `ATTRNAME_ACL`, `ATTRNAME_NTSD`, and `ATTRNAME_NTSD_FULL`; the attribute name selects the kernel CIFS SMB security-info flags. SID parsing is delegated to the idmap plugin through `init_plugin`, `str_to_sid`, and `exit_plugin` when available, with `raw_str_to_sid` as fallback.

Core helpers include `copy_cifs_sid`, `get_cifs_sid_size`, `get_aces_offset`, `get_aces_size`, `get_acl_revision`, `copy_sec_desc`, `copy_sec_desc_with_sid`, `copy_ace`, `compare_aces`, `alloc_sec_desc`, and the operation functions `ace_set`, `ace_add`, `ace_add_reorder`, `ace_modify`, and `ace_delete`. Command parsing is handled by `parse_cmdline_aces`, `build_cmdline_aces`, `verify_ace_type`, `verify_ace_flags`, and `verify_ace_mask`.

## Control flow
`main` parses one action option, optional `-U`, and a target path. For ACE actions it counts and tokenizes comma-separated `ACL:SID:TYPE/FLAGS/MASK` entries, converts SIDs, validates type/flag/mask values, then loops over `getxattr` with increasing buffers until the descriptor fits or `XATTR_SIZE_MAX` is reached. Owner/group changes fetch `system.cifs_ntsd`, rebuild owner/group layout with an unchanged DACL, and write the descriptor. ACE changes fetch either DACL or SACL information, build fetched ACE copies, apply the selected mutation, rebuild descriptor offsets and ACL headers, then call `setxattr`.

## State and persistence behavior
The persistent state is the server-backed NT security descriptor reachable through CIFS xattrs. The utility mutates file metadata on a mounted CIFS share and has no separate local state. It must preserve endian encoding, SID lengths, ACL counts, and descriptor offsets, including Azure-style descriptors where owner/group SIDs can trail ACLs.

## Dependencies and integration points
It integrates with the kernel CIFS client xattr ABI, SMB servers that honor security descriptor updates, and the cifs-utils idmap plugin. It uses libc endian conversion, getopt, xattr APIs, and constants from CIFS ACL headers. Runtime behavior depends heavily on mount options such as `cifsacl` and on the user credentials used for the mounted share.

## Risks
The code performs manual binary layout construction with limited bounds validation. Risks include malformed server descriptors causing offset mistakes, allocation sizes based on simplified maximum ACE sizes, memory leaks in `build_reorder_aces` because only pointer arrays are freed after deep copies, and compatibility issues around SACL writes requiring `system.cifs_ntsd_full`. `verify_ace_type` contains a typo for `MANDATODY_LABEL`, so the documented SACL `MANDATORY_LABEL` spelling may not parse. The owner/group path reads `num_aces` with `le16toh` even though other code treats it as 32-bit, which is a signal to test against real descriptors.

## Test signals
Useful tests include raw SID parsing, name-to-SID plugin fallback, DACL add/delete/modify/set, `-A` canonical ordering, SACL `-U` operations, owner/group replacement with different SID lengths, empty DACL handling, large descriptor buffer growth, Azure-style descriptor offsets, invalid ACE forms, and verifying resulting ACLs with `getcifsacl` or `smbinfo secdesc` on a CIFS mount.
