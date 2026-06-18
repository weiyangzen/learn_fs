# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/icount.h

Read coverage: complete file read, 46 lines.

Purpose: declares fsck inode-count table abstraction.

Key data:
- `o2fsck_icount` combines a bitmap for count-one inodes with an rb-tree for higher counts.

Key API: set, get, delta, allocate, free, and find-next helpers.

Dependencies: OCFS2 bitmap API and kernel rbtree API.
