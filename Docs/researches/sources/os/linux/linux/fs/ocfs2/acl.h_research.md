# File Research: sources/os/linux/linux/fs/ocfs2/acl.h

## Role

Declares OCFS2 ACL on-disk entry format and ACL helper APIs used by OCFS2 inode/xattr/create/chmod paths.

## Major Contents

- Header guard `OCFS2_ACL_H`.
- Includes `linux/posix_acl_xattr.h`.
- `struct ocfs2_acl_entry`:
  - Little-endian tag, permission, and ID fields.
- Function prototypes:
  - `ocfs2_iop_get_acl()`
  - `ocfs2_iop_set_acl()`
  - `ocfs2_acl_chmod()`
  - `ocfs2_init_acl()`

## Important Invariants

- OCFS2 ACL xattr entries are little-endian on disk.
- Callers pass OCFS2 transaction/buffer/allocation context to `ocfs2_init_acl()` so ACL inheritance can participate in inode creation journaling.

## Dependencies

- Requires POSIX ACL xattr definitions and OCFS2 types declared elsewhere, such as `handle_t`, `ocfs2_alloc_context`, `inode`, and `buffer_head`.

## Notes For Future Work

- This is a small interface header; behavior lives in `acl.c`.
