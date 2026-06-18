# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/rpc.c

Purpose: SunRPC/XDR-ish marshal/unmarshal helpers and common RPC reply utilities.

Key behavior: `rpcM2S` decodes UDP header-prefixed RPC calls/replies into `Rpccall`; `rpcS2M` serializes them back. `auth2unix` decodes AUTH_UNIX, `string2S` decodes counted strings into interned strings, `rpcprint` and `showauth` log decoded calls, and `garbage`/`error` build failure replies.

Integration notes: uses big-endian network integer macros and Plan 9 UDP header layout. `string2S` allocates temporary NUL-terminated storage and interns it through `strstore`.
