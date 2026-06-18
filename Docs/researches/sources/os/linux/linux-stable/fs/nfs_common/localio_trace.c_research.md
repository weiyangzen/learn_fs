# File Research: sources/os/linux/linux-stable/fs/nfs_common/localio_trace.c

Purpose: Instantiates NFS LOCALIO tracepoints.

Key responsibilities:
- Defines `CREATE_TRACE_POINTS` and includes `localio_trace.h`.

Integration:
- Built with localio common support.
- Provides tracepoint definitions used by `nfslocalio.c`.

Risks and notes:
- Must be compiled exactly once to materialize tracepoints.
