# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/authhostowner.c

This file authenticates a `Session` to a 9P server using factotum-backed auth proxying.

Key routines:
- `gstring` and `gcarray` parse counted strings/byte arrays from buffers, though they are local helpers not used by the main path here.
- `dorpc` wraps `auth_rpc`, handling `ARneedkey`/`ARbadkey` by invoking an optional key callback.
- `doread` and `dowrite` perform 9P reads/writes on an auth fid.
- `authproto` proxies an auth conversation between factotum RPC and a 9P auth fid until `auth_getinfo` succeeds or an error occurs.
- `authhostowner` obtains an auth fid with `Tauth`, opens `/mnt/factotum/rpc`, runs `p9any` as client, then tries `Tattach` with the auth fid.

Important interactions:
- Uses `xmesg`, `newfid`, `putfid`, and 9P request fields in `Session.f`.
- Uses Plan 9 auth APIs: `auth_allocrpc`, `auth_rpc`, `auth_getkey`, `auth_getinfo`, and cleanup helpers.
- Called during service initialization in `nfsmount.c:srvinit`.

Research notes:
- If `Tauth` fails, it treats authentication as unneeded and returns success.
- Always cleans/clunks auth and attach fids on exit paths.
