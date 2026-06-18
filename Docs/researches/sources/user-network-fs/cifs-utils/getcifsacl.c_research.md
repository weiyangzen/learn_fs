<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/getcifsacl.c -->
# sources/user-network-fs/cifs-utils/getcifsacl.c

## Purpose

`getcifsacl.c` implements the `getcifsacl` CLI, which reads CIFS security descriptor xattrs and prints owner, group, DACL, SACL, ACE type/flags/masks, and SID or mapped name information.

## Important APIs, Types, and Functions

Important functions are `print_each_ace_mask`, `print_ace_mask`, `print_ace_flags`, `print_ace_type`, `print_sid`, `print_ace`, `parse_acl`, `parse_sid`, `parse_sec_desc`, `getcifsacl_usage`, `getcifsacl`, `recursive`, and `main`. It uses `struct cifs_ntsd`, `struct cifs_ctrl_acl`, and `struct cifs_ace`.

## Control Flow

`main` parses `-v`, `-r`, and `-R`, optionally initializes the idmap plugin for SID-to-name conversion, then processes each path directly or through `nftw`. `getcifsacl` attempts to read `system.cifs_ntsd_full` into a growing buffer; on insufficient privilege or unsupported SACL retrieval it falls back to `system.cifs_acl`. `parse_sec_desc` computes owner, group, DACL, and SACL pointers from little-endian offsets, prints descriptor metadata, validates SID/ACL ranges, and iterates ACEs.

## State and Persistence Behavior

The utility reads server-backed CIFS xattr state and emits text. Global process state includes `plugin_handle`, `plugin_loaded`, `execname`, and `raw`. It does not modify ACLs.

## Dependencies and Integration Points

It depends on Linux xattrs, `nftw`, endian helpers, `cifsacl.h`, and `idmap_plugin.h`. It integrates with CIFS mounts that expose `system.cifs_acl` or NTSD xattrs and the configured idmap plugin.

## Risks and Edge Cases

Descriptor parsing is pointer arithmetic over untrusted xattr data. The code checks several boundaries but computes some offset-derived pointers before validating the offsets are inside the buffer. Recursive mode does not propagate `getcifsacl` failures into `ret` in the same way direct mode does. Raw mode avoids plugin dependency.

## Test Signals

Tests should use fixture xattrs or mock `getxattr` data for owner/group/DACL/SACL, ERANGE growth, SACL EPERM/EIO fallback, malformed offsets and ACE sizes, raw mode, plugin mapping failure, recursive traversal, and big-endian conversion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/getcifsacl.c -->
