# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/pass5.h

Read coverage: complete file read, 26 lines.

Purpose: declares fsck pass 5.

API: `o2fsck_pass5(o2fsck_state *ost)`.

Role: quota-related final pass that loads, merges, recomputes, or recreates quota state.

Risk note: include guard closing comment names `PASS4_H`, likely cosmetic copy/paste mismatch.
