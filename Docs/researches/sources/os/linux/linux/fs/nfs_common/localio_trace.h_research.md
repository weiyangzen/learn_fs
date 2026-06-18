# File Research: sources/os/linux/linux/fs/nfs_common/localio_trace.h

Declares tracepoints for NFS LOCALIO client state changes.

Key behavior:
- Defines trace system `nfs_localio`.
- Declares an event class carrying the NFS client protocol version and server hostname.
- Defines `nfs_localio_enable_client` and `nfs_localio_disable_client` events from that class.
- Sets `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` so the trace generation framework can include this local header.

Important interactions:
- Used by `nfslocalio.c` to trace when a client is enabled for, or disabled from, LOCALIO protocol bypass.
