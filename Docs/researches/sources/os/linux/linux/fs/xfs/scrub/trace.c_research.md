# File Research: sources/os/linux/linux/fs/xfs/scrub/trace.c

This file instantiates XFS scrub tracepoints. It includes the XFS and scrub headers needed by trace event definitions, defines a helper used by trace formatting, then includes `scrub/trace.h` with `CREATE_TRACE_POINTS`.

Key helper:
- `xchk_btree_cur_fsbno(struct xfs_btree_cur *cur, int level)`: computes the filesystem block number for a btree cursor level.
  - Uses the buffer at that level if present.
  - For inode-rooted btrees at root level, returns the inode’s containing block.
  - Returns `NULLFSBLOCK` otherwise.

Tracepoint instantiation:
- `#define CREATE_TRACE_POINTS`
- `#include "scrub/trace.h"`

Dependencies:
- Pulls in inode, btree, AG, realtime bitmap, quota, directory, rmap, parent, metadata-file, rtgroup, and scrub helper headers so trace events can access field definitions.
- Includes `scrub/xfarray.h`, `scrub/xfblob.h`, `scrub/iscan.h`, `scrub/orphanage.h`, `scrub/nlinks.h`, `scrub/fscounters.h`, and bitmap/dirtree helpers for trace data structures.

Risk notes:
- This file should remain the single tracepoint-definition translation unit; other users include `trace.h` without `CREATE_TRACE_POINTS`.
- The helper exists so trace events can render btree cursor locations consistently without duplicating cursor logic in the generated trace code.
