<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifsacl.h -->
# sources/user-network-fs/cifs-utils/cifsacl.h

## Purpose

`cifsacl.h` defines CIFS/NTFS ACL constants, xattr names, ACE kind classification, and packed security descriptor structures used by ACL utilities.

## Important APIs, Types, and Functions

Important definitions include `ATTRNAME_ACL`, `ATTRNAME_NTSD`, `ATTRNAME_NTSD_FULL`, file/standard/generic access masks, common composite masks such as `FULL_CONTROL`, `EREAD`, and `CHANGE`, ACE flags, ACE types, comparison bitmasks, `DEFAULT_ACL_REVISION`, `ace_kinds`, `struct cifs_ntsd`, `struct cifs_ctrl_acl`, and `struct cifs_ace`.

## Control Flow

The header has no executable flow. `getcifsacl.c` reads packed descriptors through these structures and prints owner, group, DACL, and SACL fields. `setcifsacl.c` in the broader tree uses the same constants for construction and comparison.

## State and Persistence Behavior

The structures represent on-the-wire or xattr-backed little-endian data obtained from the CIFS client. Persistent state is the server-side security descriptor surfaced through CIFS xattrs; the header only describes the layout.

## Dependencies and Integration Points

It includes `cifsidmap.h` for SID layout. It integrates with Linux extended attributes `system.cifs_acl`, `system.cifs_ntsd`, and `system.cifs_ntsd_full` and with idmap plugins for SID-to-name presentation.

## Risks and Edge Cases

The structures are packed and multi-byte fields are little-endian. Callers must bounds-check every offset and ACE size before dereferencing. `DACL_VTYPES` and `SACL_VTYPES` are bitwise ORs of numeric type values rather than masks indexed by type, so callers should use them carefully.

## Test Signals

Tests should parse sample security descriptors with owner/group/DACL/SACL, unknown ACE types, maximum SID subauthorities, raw and mapped output, and endian conversions on big-endian build targets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifsacl.h -->
