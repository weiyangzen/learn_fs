## sources/user-network-fs/nfs-ganesha/src/FSAL/posix_acls.c

### Purpose
`posix_acls.c` converts between POSIX draft ACLs, FSAL/NFSv4 ACL representations, and Linux POSIX ACL xattr wire format. It implements the NFSv4-to-POSIX mapping strategy referenced by the file comments and preserves mask/deny semantics where possible.

### Important APIs, Types, And Functions
ACE classification helpers are `is_ace_valid_for_effective_acl_entry`, `is_ace_valid_for_inherited_acl_entry`, `isallow`, and `isdeny`. POSIX ACL entry helpers include `ace_count`, `find_entry`, and `get_entry`. Main conversion functions are `posix_acl_2_fsal_acl` and `fsal_acl_2_posix_acl`. Xattr helpers are `posix_acl_xattr_size`, `posix_acl_entries_count`, `xattr_2_posix_acl`, and `posix_acl_2_xattr`.

### Control Flow
POSIX-to-FSAL conversion first reads mask and other entries, then walks POSIX ACL entries and emits one or two FSAL ACEs per entry. It sets special IDs for owner/group/everyone/mask, group flags for group entries, inheritance flags for default ACLs, allow permissions from POSIX read/write/execute bits, mask-deny iflags when the POSIX mask suppresses permissions, and explicit deny ACEs when later entries or `other` allow permissions not granted to the current entry. FSAL-to-POSIX conversion builds separate allow and deny ACLs, precomputes `EVERYONE@` allow/deny effects, ensures required `USER_OBJ` and `GROUP_OBJ` entries, processes applicable effective or inherited ACEs, creates user/group/mask entries as needed, calculates a mask if needed, checks the resulting ACL, and returns the allow ACL. Xattr conversion validates header size/version/endian fields and serializes/deserializes tag, permission, and qualifier IDs.

### State And Persistence
The file allocates and frees POSIX ACL objects and temporary text/debug buffers. It does not maintain global state. Xattr conversion reads and writes caller-provided buffers using little-endian ACL structures suitable for persistent extended attributes.

### Dependencies And Integration Points
It depends on `posix_acls.h`, libacl APIs, FSAL ACE macros, endian helpers, and FSAL logging. VFS-style FSALs use it when exposing NFSv4 ACLs over POSIX ACL capable backends or translating stored POSIX ACL xattrs into FSAL ACL attributes.

### Risks
ACL mapping is inherently lossy between NFSv4 and POSIX models; deny ordering, inheritance, special IDs, and mask behavior can produce surprising results. `fsal_acl_2_posix_acl` has a FIXME about allocating maximum possible entries and possible leaks; some error paths return without freeing both ACLs. `get_entry` returns NULL on qualifier set failure without deleting the new entry. Xattr parsing must reject malformed sizes and unknown tags; otherwise ACLs could be misinterpreted. Macro-heavy conditions such as `if IS_FSAL_ACE_READ_DATA (*f_ace)` rely on unusual macro syntax and need compiler coverage.

### Test Signals
Tests should round-trip simple owner/group/other ACLs, named users/groups with masks, deny ACEs, inherited/default ACLs, directory write/delete-child behavior, `EVERYONE@` deny interactions, xattr size/count validation, endian serialization, malformed tags/version/size rejection, and debug string paths under `COMPONENT_FSAL`.
