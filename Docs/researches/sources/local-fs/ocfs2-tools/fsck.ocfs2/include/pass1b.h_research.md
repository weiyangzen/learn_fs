# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/pass1b.h

Read coverage: complete file read, 24 lines.

Purpose: declares duplicate-cluster repair pass.

API: `ocfs2_pass1_dups(o2fsck_state *ost)`.

Role: handles overclaimed clusters detected during pass 1, including clone/delete/refcount-oriented repairs.

Risk note: include guard closing comment names `PASS1_H`, likely a cosmetic copy/paste mismatch.
