# File Research: sources/local-fs/ocfs2-tools/include/o2dlm/o2dlm.h

This is the public userspace API for OCFS2 DLM locking through dlmfs/stack glue.

Key content:
- Defines max lock ID length, max domain length, full domain path length, valid flags, and lock levels.
- Forward-declares `struct o2dlm_ctxt`.
- Declares `o2dlm_initialize()` and `o2dlm_destroy()`.
- Declares lock/unlock/drop-lock APIs.
- Declares `o2dlm_lock_with_bast()` and `o2dlm_process_bast()` for blocking AST notification through a pollable file descriptor.
- Declares LVB read/write APIs.
- Declares optional feature probes for BAST and stackglue support.

Integration notes:
- Includes generated `o2dlm_err.h`.
- API users must respect lock ID and domain length constraints.
