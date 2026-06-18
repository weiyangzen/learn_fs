# File Research: sources/os/plan9/9front/sys/src/lib9p/auth.c

## Read Status
Complete: 203 lines read.

## Purpose
Implements lib9p authentication support using Plan 9 factotum. It handles `Tauth` setup, auth fid reads/writes, auth fid destruction, and authenticated attach validation.

## Main Responsibilities
- Allocate an auth helper state (`Afid`) for each auth fid.
- Open `/mnt/factotum/rpc` and start a factotum auth protocol.
- Expose auth RPC exchange over 9P read/write on `QTAUTH` fids.
- Verify returned `AuthInfo` user identity against requested uname.
- Ensure `Tattach` uses the same uname/aname and has completed authentication.

## Important Functions
- `auth9p`: initializes factotum auth RPC state and returns an auth qid.
- `_authread`: internal auth RPC read step; marks authentication complete on `ARdone`.
- `authread`: 9P auth fid read handler.
- `authwrite`: 9P auth fid write handler.
- `authdestroy`: frees auth RPC state attached to a fid.
- `authattach`: validates an attach against a completed auth fid.

## Dependencies and Interactions
- Uses `<auth.h>` and factotum RPC APIs: `auth_allocrpc`, `auth_rpc`, `auth_getinfo`, `auth_freerpc`.
- Intended to be wired into `Srv.auth`, `Srv.read`, `Srv.write`, and fid destroy paths.
- Shares response flow with `respond` and `responderror` from `srv.c`.

## Notes
- `authgen` generates synthetic auth qid paths starting in the high path range.
- Authentication defaults to `proto=p9any role=server` unless `srv->keyspec` is set.
