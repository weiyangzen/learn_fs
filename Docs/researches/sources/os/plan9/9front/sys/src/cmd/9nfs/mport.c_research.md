# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/mport.c

This standalone utility queries a remote NFS mount service through the portmapper.

Key behavior:
- Dials UDP port 111 on a host, enables header mode, and parses remote IP/port from the network directory.
- Sends a portmapper `GETPORT` request for mount program `100005`, version 1, UDP.
- Sends mount `NULL` and `EXPORT` RPCs to the returned mount port.
- Prints exported directories and access groups.
- Optionally emits AUTH_UNIX credentials through `putauth` when `-m mach` is supplied.

Key routines:
- `main` drives portmapper and mount RPC sequence.
- `putauth` builds an AUTH_UNIX credential blob.
- `rpccall` serializes, sends, reads, parses, validates, and returns result length.

Important interactions:
- Uses shared RPC packing/parsing macros and `rpcS2M`/`rpcM2S`.
- Debug output is controlled by `rpcdebug`.

Research notes:
- This is a diagnostic/client tool, not part of the main NFS server loop.
