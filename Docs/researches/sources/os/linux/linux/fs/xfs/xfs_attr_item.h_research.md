# File Research: sources/os/linux/linux/fs/xfs/xfs_attr_item.h

Defines kernel-only structures and APIs for logged deferred attribute intent/done items.

Key elements:
- `struct xfs_attri_log_nameval` stores kvecs for name, optional new name, value, optional new value, and a refcount; payload data follows the structure.
- `struct xfs_attri_log_item` wraps a log item, reference count, shared name/value buffer, and ATTRI log format.
- `struct xfs_attrd_log_item` wraps a done log item, backpointer to ATTRI, and ATTRD log format.
- Declares `xfs_attri_cache` and `xfs_attrd_cache`.
- Defines `enum xfs_attr_defer_op` for set, remove, and replace.
- Declares `xfs_attr_defer_add`.

Dependencies:
- Consumed by deferred xattr code and log item implementation in `xfs_attr_item.c`.

Research notes:
- Comments document that ATTRI records work to be done and ATTRD records completion.
- The trailing-buffer design is central to sharing large names/values across deferred state and log items.
