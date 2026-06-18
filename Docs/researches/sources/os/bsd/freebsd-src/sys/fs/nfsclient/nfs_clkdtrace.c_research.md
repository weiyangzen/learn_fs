# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clkdtrace.c

`nfs_clkdtrace.c` implements the FreeBSD DTrace provider `nfscl` for NFS client logical RPC and cache events.

Key contents:
- Defines DTrace provider attributes and provider operations (`provide`, `enable`, `disable`, `getargdesc`, `destroy`).
- Defines `struct dtnfsclient_rpc`, mapping a logical NFS operation slot to NFSv4, NFSv3, and optional NFSv2 probe names and storing start/done probe ids.
- Defines the procedure-name table indexed by NFS procedure number up to `NFSV41_NPROCS + 1`, covering v2/v3/v4 operations and a final noop slot.
- Registers access-cache probes: flush done, get hit, get miss, load done.
- Registers attribute-cache probes: flush done, get hit, get miss, load done.
- Registers NFSv2, NFSv3, and NFSv4 RPC start/done probes, using sparse v2/v3 names and v4 names.
- `dtnfsclient_getargdesc()` describes probe argument types for cache probes and RPC probes. RPC done probes expose an additional integer error/status argument.
- `dtnfsclient_enable()` and `dtnfsclient_disable()` set per-probe function pointers or per-procedure probe ids used by the runtime NFS client code.
- `dtnfsclient_load()` registers the provider and installs generic NFS start/done probe function pointers.
- `dtnfsclient_unload()` clears function pointers and unregisters the provider.
- Module metadata declares dependencies on `dtrace`, `opensolaris`, `nfscl`, and `nfscommon`.

Important integration points:
- Probe arrays (`nfscl_nfs2_start_probes`, etc.) are externally allocated by the client; this provider fills ids into them.
- Procedure table sizing is tied to protocol counts from `nfsproto.h`.
- The provider traces logical NFS client operations, not necessarily one-to-one network RPC sends; comments explicitly mention auth retries, jukebox retries, and cache hits.

Research notes:
- This file is observability infrastructure. It should track procedure table changes when protocol procedure counts/names are extended.
- Incorrect argument descriptions can break DTrace consumers even if NFS behavior remains correct.
