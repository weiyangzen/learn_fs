# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/server.c

Shared RPC server loop for Plan 9 NFS/portmapper-style services, supporting UDP and TCP transports.

Key responsibilities:
- Parses common server flags through `argopt`: 9P debug, no reply cache, RPC debug, reject all, TCP mode, and chatty logging.
- Daemonizes with `rfork`, starts a periodic alarm helper, initializes program maps, then serves either UDP or TCP.
- Opens UDP in header mode and accepts TCP connections, adapting TCP connections to an RPC-like header context.
- Decodes RPC calls, validates version, dispatches by program/version/procedure, and encodes accepted/denied replies.
- Maintains a small duplicate-reply cache keyed by remote IP, port, and xid.
- Implements TCP record-marker framing for RPC over TCP.
- Caches DNS reverse lookups and strips local hostname prefixes through `getdnsdom`/`getdom`.
- Installs `%I` formatting for dotted IPv4 addresses.

Dependencies:
- Uses `Rpccall`, `Progmap`, `Procmap`, `Rpccache`, `Udphdr`, `rpcM2S`, `rpcS2M`, and `rpcprint` from the 9nfs subsystem.
- Uses Plan 9 network files (`announce`, `listen`, `accept`, `/net` endpoint files), `csgetvalue`, and formatting hooks.

Notable risks:
- Fixed 9000-byte request/reply buffers bound all RPC payloads.
- Reply caching is global and small (`MAXCACHE` 64).
- The DNS cache is unbounded and never expires.
- Several paths continue after malformed or non-call messages instead of closing the client, matching UDP-style service behavior.
