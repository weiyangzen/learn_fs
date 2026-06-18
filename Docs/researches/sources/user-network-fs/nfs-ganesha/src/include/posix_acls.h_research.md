# sources/user-network-fs/nfs-ganesha/src/include/posix_acls.h

## Purpose
This header declares conversion utilities between Ganesha FSAL/NFSv4 ACLs, POSIX ACLs, and Linux xattr ACL encodings.

## Important APIs, Types, And Control Flow
It defines inheritance/applicability macros for FSAL ACE flags, default permission masks, xattr names `system.posix_acl_access` and `system.posix_acl_default`, and `ACL_FOR_V4`/`ACL_FOR_V3`. It declares `struct acl_ea_entry`, `struct acl_ea_header`, `posix_acl_2_fsal_acl`, `fsal_acl_2_posix_acl`, entry lookup/creation helpers, ACL entry counting, xattr size/count helpers, and xattr serialization/deserialization. Inline `posix_acl_get_uid` and `posix_acl_get_gid` read and free ACL qualifiers.

## State And Persistence
The header has no global state. Its implementations allocate ACL objects and FSAL ACE arrays and serialize to xattr buffers that can be persisted by filesystem xattr calls.

## Dependencies And Integration Points
It depends on `<sys/acl.h>`, `<acl/libacl.h>`, `nfs4_acls.h`, and `fsal_types.h`. It integrates NFSv3/v4 ACL behavior with POSIX ACL storage and FSAL object attributes.

## Risks And Test Signals
ACL mapping is security-sensitive; inheritance flags, owner/group qualifiers, mask entries, and deny/allow conversion must be exact. Tests should cover directory default ACLs, files without ACLs, malformed xattr sizes, qualifier allocation failures, round-trips between FSAL and POSIX ACLs, and permission equivalence for common NFSv4 ACE sets.
