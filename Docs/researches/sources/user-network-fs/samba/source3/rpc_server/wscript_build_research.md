# sources/user-network-fs/samba/source3/rpc_server/wscript_build

## Purpose
`wscript_build` defines the source3 RPC server build graph: the main DCERPC host binary, shared worker library, per-service rpcd helper binaries, RPC server framework subsystems, individual RPC service subsystems, Spotlight/mdssvc variants, and the aggregate `RPC_SERVICE` dependency set.

## Important APIs, types, and functions
- `bld.SAMBA_BINARY('samba-dcerpcd', ...)` builds the installed source3 DCERPC host.
- `bld.SAMBA_LIBRARY('RPC_WORKER', private_library=True, ...)` builds common worker support used by rpcd helpers.
- `bld.SAMBA3_BINARY(...)` defines installed service workers such as `rpcd_classic`, `rpcd_lsad`, `rpcd_spoolss`, `rpcd_epmapper`, `rpcd_fsrvp`, `rpcd_witness`, and `rpcd_mdssvc`.
- `bld.SAMBA3_SUBSYSTEM(...)` defines service libraries such as `RPC_DSSETUP`, `RPC_EPMAPPER`, `RPC_EVENTLOG`, `RPC_NETDFS`, `RPC_WKSSVC`, and `RPC_WITNESS`.
- Conditional build flags include `enabled=bld.env.with_ctdb` for Witness and `bld.env.spotlight_backend_es` for Elasticsearch-backed mdssvc sources and installed mappings.

## Control flow
The file is evaluated by waf during configuration/build. It first declares core RPC host and worker components, then service-specific worker binaries, then framework subsystems, then each RPC service subsystem. Finally it assembles `RPC_SERVICE`, which pulls together the classic in-process service set used by `rpcd_classic`, and defines the socket helper subsystem.

## State and persistence behavior
This file does not manage runtime state. Its persistent effect is the build artifact graph and install layout under `${SAMBA_LIBEXECDIR}` and `${SAMBA_DATADIR}`. Conditional settings decide whether CTDB Witness and Elasticsearch mdssvc support are compiled and installed.

## Dependencies and integration points
It is the integration point between source files under `source3/rpc_server/*`, generated NDR libraries, `smbd_base`, `RPC_WORKER`, service-specific dependencies such as `LIBNET`, `PRINTING`, `LIBCLI_WINREG_INTERNAL`, `samba-cluster-support`, and optional Spotlight/Elasticsearch dependencies.

## Risks and edge cases
- Missing dependencies here surface as link failures or runtime helper binaries without required service symbols.
- `rpcd_witness` and `RPC_WITNESS` are CTDB-gated; non-CTDB builds will not have Witness service support.
- The aggregate `RPC_SERVICE` includes many services but not every standalone rpcd binary, so changing service placement can affect classic vs external RPC worker behavior.
- Optional mdssvc source/dependency expansion must stay synchronized with installed data files.

## Test signals
Build validation should cover default builds, CTDB-enabled builds, and Spotlight Elasticsearch builds. Runtime smoke tests should verify expected rpcd binaries are installed and that `rpcd_classic` links the aggregate service set.
