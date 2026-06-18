# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/o2fsck_strings.h

Read coverage: complete file read, 44 lines.

Purpose: declares rb-tree-backed string set helpers used by fsck for duplicate-name detection.

Key data:
- `o2fsck_strings` stores a root node and byte-allocation accounting.

Key API: existence test, insert with duplicate result, init, free, and allocated-byte reporting.

Dependencies: OCFS2 and kernel rbtree headers.
