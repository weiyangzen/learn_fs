# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/refcount.h

Read coverage: complete file read, 33 lines.

Purpose: declares fsck refcount-tree validation and accounting APIs.

Key API:
- `o2fsck_check_refcount_tree()`
- `o2fsck_mark_clusters_refcounted()`
- `o2fsck_check_mark_refcounted_clusters()`

Role: supports reflink/refcounted extent validation and detects whether refcount records match physical cluster sharing.
