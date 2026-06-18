# File Research: sources/os/linux/linux-stable/fs/ocfs2/xattr.h

## Scope

This header declares OCFS2 xattr types, VFS xattr handlers, security-xattr state, public xattr operations, refcount/reflink hooks, and the value-buffer wrapper shared by xattr implementation code.

## APIs And Structures

- `enum ocfs2_xattr_type` defines on-disk namespace indexes for user, POSIX ACL access/default, trusted, security, and max sentinel.
- `ocfs2_security_xattr_info` carries security initialization state: enable flag, name, allocated value, and value length.
- Declares exported handlers: `ocfs2_xattr_user_handler`, `ocfs2_xattr_trusted_handler`, `ocfs2_xattr_security_handler`, and `ocfs2_xattr_handlers`.
- Declares main operations: list, get without locks, set, create-time set with existing transaction, inline-outside check, remove, security get/set, init credit calculators, refcount attach, reflink, and post-reflink security/ACL initialization.
- `ocfs2_xattr_value_buf` bundles a buffer head, journal access callback, and `ocfs2_xattr_value_root *` so generic value-tree code can operate on inline, block, or bucket storage.

## Dependencies And Notes

- Depends on Linux xattr definitions plus OCFS2 types such as `handle_t`, `ocfs2_alloc_context`, `ocfs2_dinode`, `ocfs2_caching_info`, and cached dealloc contexts.
- The comment above `ocfs2_xattr_value_buf` explains the core design used by `xattr.c`: xattr values can be stored in multiple physical containers but are manipulated through a common wrapper.
