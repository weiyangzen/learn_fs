# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/portmapper.c

SunRPC portmapper service for the 9nfs suite.

Key responsibilities:
- Defines static RPC program/version/protocol-to-port mappings for NFSv2, mount, and pcnfsd.
- Exports RPC program `100000` version `2` on UDP port `111`.
- Implements portmapper procedures: null, set, unset, getport, dump, and callit.
- Delegates daemon setup and packet serving to the shared `server()` RPC framework.

Important behavior:
- `pmapset()` always returns false and `pmapunset()` always returns true; the static map is not mutated.
- `pmapgetport()` decodes four 32-bit arguments but only uses program, version, and protocol.
- `pmapdump()` serializes the full static mapping list.
- `pmapcallit()` only answers when the mapped procedure is zero and returns the mapped port plus an empty result, not a proxied RPC call.

Dependencies:
- Uses `all.h`, `rpc.h` XDR-style macros, `Progmap`, `Procmap`, `Rpccall`, and shared logging/error helpers.

Notable risks:
- Hard-coded ports must stay aligned with the actual NFS/mount/pcnfsd services.
- Request length checks are strict but parsing assumes `rpcM2S()` already supplied a sane argument buffer.
