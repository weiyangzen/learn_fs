# File Research: sources/local-fs/ocfs2-tools/libocfs2/refcount.h

Small internal header for refcount post-operation callbacks.

Definitions:
- `ocfs2_post_refcount_func` is a callback type taking `ocfs2_filesys *fs` and opaque `void *para`.
- `struct ocfs2_post_refcount` stores a callback and its parameter.

Purpose:
- Used by `refcount.c` during CoW/refcount operations when callers need extra work after the data b-tree is modified but before the larger operation is considered complete.
- The xattr bucket CoW path uses this to write an entire xattr bucket after refcount and extent updates succeed.

Scope:
- Header is intentionally minimal and private to libocfs2 refcount implementation details.
