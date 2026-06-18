# File Research: sources/os/linux/linux/fs/nfs_common/localio_trace.c

Instantiates tracepoints for NFS LOCALIO client enable/disable events.

Key behavior:
- Includes NFS and namei headers needed by trace definitions.
- Defines `CREATE_TRACE_POINTS` before including `localio_trace.h`, causing the tracepoint storage and metadata to be emitted in this compilation unit.

Important interactions:
- Built into `nfs_localio.o` with `nfslocalio.o`.
- Tracepoint definitions are declared in `localio_trace.h` and used by LOCALIO client lifecycle code.
