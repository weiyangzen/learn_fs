# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/mport.c

Purpose: diagnostic RPC client for querying a remote portmapper and mount daemon.

Key behavior: dials UDP portmapper, enables header mode, extracts remote host/port, calls `PMAPPROC_GETPORT` for mount, pings mount null, then requests and prints exports. Optional `-m` creates AUTH_UNIX credentials.

Integration notes: standalone test/tool using shared RPC codec. Exercises `rpcS2M`, `rpcM2S`, and mount export parsing.
