# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_trace.c

Tracepoint instantiation unit for XFS.

Key behavior:
- Includes the broad set of XFS headers needed by trace event definitions.
- Defines `CREATE_TRACE_POINTS` immediately before including `xfs_trace.h`.
- This causes tracepoint storage and trace event implementations declared in `xfs_trace.h` to be emitted exactly once.

Research notes:
- The include order is intentional: helper types and functions must be visible before trace event implementation generation.
- This file contains no runtime logic beyond tracepoint definition instantiation, but many XFS source files depend on the generated tracepoints.
