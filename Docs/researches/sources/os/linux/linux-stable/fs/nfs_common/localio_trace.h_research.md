# File Research: sources/os/linux/linux-stable/fs/nfs_common/localio_trace.h

Purpose: Defines trace events for NFS LOCALIO client enable/disable.

Key responsibilities:
- Declares trace system `nfs_localio`.
- Defines event class `nfs_local_client_event` capturing NFS protocol version and server hostname.
- Defines `nfs_localio_enable_client` and `nfs_localio_disable_client`.

Integration:
- Included by `localio_trace.c` to instantiate and by `nfslocalio.c` to emit events.
- Uses standard Linux tracepoint infrastructure and NFS/SUNRPC trace helpers.

Risks and notes:
- Trace include path/file macros are set for local header generation.
