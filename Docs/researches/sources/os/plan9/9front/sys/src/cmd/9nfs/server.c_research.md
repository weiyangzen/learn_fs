# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/server.c

Shared SunRPC server runtime for 9nfs daemons, with UDP/TCP listeners, dispatch, DNS cache, and duplicate-reply cache.

Key responsibilities:
- Parses common daemon flags through `argopt()`.
- Daemonizes, initializes program maps, and starts UDP or TCP service.
- Announces UDP sockets with header mode or accepts TCP connections and synthesizes UDP-style endpoint headers.
- `servemsg()` decodes RPC calls, validates RPC version/auth policy, dispatches to `Progmap`/`Procmap`, serializes replies, and caches them.
- Supports TCP record-mark read/write framing.
- Maintains a small DNS name cache and maps client IPs to domain names.
- Maintains an LRU cache of up to 64 replies by host, port, and XID.

Important behavior:
- `rejectall` forces `AUTH_TOOWEAK`.
- Program mismatch replies report observed low/high versions.
- Procedure handlers return negative length to suppress reply.
- The alarm helper process sets `alarmflag`; `servemsg()` invokes `rpcalarm` lazily between messages.
- TCP children process one accepted connection until EOF/error.

Dependencies:
- Uses Plan 9 network APIs (`announce`, `listen`, `accept`), `ndb` lookup, `rpcM2S()`, `rpcS2M()`, `rpcprint()`, and global buffers from this file.

Notable risks:
- Global buffers and reply cache fit the single-threaded UDP path but require care around forked TCP children.
- Reply-cache keys ignore RPC program/procedure and depend on XID uniqueness per client endpoint.
- `getdnsdom()` writes `name[len] = 0` after copying `len-1`, which is off by one for the passed buffer length.
