# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clkdtrace.c

This file defines the `dtnfscl` DTrace provider for the NFS client. It exposes logical client RPC probes and cache probes for access-cache and attribute-cache activity.

Key components:
- `dtnfsclient_rpcs[]` maps NFS procedure slots to NFSv2, NFSv3, and NFSv4 probe names.
- `dtnfsclient_getargdesc()` describes probe argument types.
- `dtnfsclient_provide()` creates probes for access cache, attribute cache, and NFSv2/v3/v4 RPC start/done events.
- `dtnfsclient_enable()` and `dtnfsclient_disable()` install or clear function pointers/probe IDs used by NFS client tracing macros.
- `dtnfsclient_load()` registers provider `nfscl`.
- `dtnfsclient_unload()` unregisters it and clears generic NFS RPC probe hooks.
- `dtnfsclient_modevent()` is a minimal module event handler.

Probe model:
- Cache probes cover access-cache flush/get hit/get miss/load done and attribute-cache flush/get hit/get miss/load done.
- RPC probes expose per-version start and done events. Done probes include an additional integer status argument.
- Sparse v2/v3/v4 naming is handled by nullable name fields in `dtnfsclient_rpcs[]`.

Dependencies:
- Uses NetBSD/FreeBSD-style DTrace provider interfaces from `dtrace_bsd.h`.
- Connects to global probe ID arrays such as `nfscl_nfs3_start_probes[]` and function pointers declared in `nfs_kdtrace.h`.
- Declares module dependencies on `dtrace`, `opensolaris`, `nfscl`, and `nfscommon`.

Research notes:
- This file does not implement NFS behavior; it instruments behavior implemented elsewhere.
- The important coupling is that probe IDs are stored in NFS client arrays, while cache probes are enabled by replacing function pointers with `dtrace_probe`.
