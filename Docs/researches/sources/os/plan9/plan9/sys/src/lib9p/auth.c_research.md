# File Research: sources/os/plan9/plan9/sys/src/lib9p/auth.c

This file implements factotum-backed 9P authentication support for lib9p servers.

Key behavior:
- Defines per-auth-fid `Afid` state containing an `AuthRpc`, requested user/aname, completion flag, and factotum fd.
- `auth9p` allocates an auth fid, opens `/mnt/factotum/rpc`, starts an auth RPC using `Srv.keyspec` or default `proto=p9any role=server`, assigns a synthetic `QTAUTH` qid, and attaches `Afid` to the fid.
- `_authread` drives the factotum read phase, copies challenge data to the client, and marks auth successful once `auth_getinfo` succeeds.
- `authread` and `authwrite` expose auth fid I/O through normal 9P read/write requests.
- `authdestroy` frees auth RPC state, strings, and fd when an auth fid is destroyed.
- `authattach` validates that attach uses a completed auth fid and that uname/aname match the original auth request.

Important dependencies:
- Plan 9 auth APIs: `auth_allocrpc`, `auth_rpc`, `auth_getinfo`, `auth_freerpc`.
- lib9p request/fid lifecycle: `Req`, `Fid`, `respond`, `responderror`.

Notable details:
- `authgen` starts at the high bit and increments for distinct auth qid paths.
- Attach can force completion by calling `_authread` with a zero-length buffer if authentication has not yet reached `ARdone`.
