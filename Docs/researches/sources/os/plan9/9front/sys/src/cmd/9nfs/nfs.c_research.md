# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/nfs.c

This file contains core NFS-to-9P object translation helpers.

Key routines:
- `rpc2xfid` converts an NFS file handle plus AUTH_UNIX credentials into an `Xfid`, validating file-handle tags, resolving `Xfile`, mapping client UID to a Plan 9 user, and optionally statting the target.
- `setuser` recursively walks/creates per-user fids from parent `Xfile` state.
- `xfstat` stats a 9P-backed `Xfid`, or fabricates stat data for authentication pseudo-files.
- `xfwstat` writes stat changes through 9P `Twstat`.
- `xfopen` opens an `Xfid`, creating a duplicate/open fid as needed and tracking mode.
- `xfclose` and `xfclear` close and release cached fids.
- `xfwalkcr` performs 9P walk or create and updates `Xfile`/`Xfid` caches.
- `xpclear` recursively clears cached namespace state.
- `xp2fhandle` encodes an `Xfile` into a 32-byte NFS file handle.
- `dir2fattr` converts Plan 9 `Dir` metadata into NFS v2 file attributes.
- `convM2sattr` parses NFS setattr data.

Important interactions:
- Used heavily by `nfsserver.c`.
- Bridges `Rpccall`, `Authunix`, `Unixidmap`, `Session`, `Xfile`, `Xfid`, and 9P `Fcall` state.
- Uses `starttime` and `Session*` pointer values in non-root file handles.

Research notes:
- Root handles contain a service name; non-root handles contain a starttime tag, session pointer, qid path, and qid type.
- UID translation is mandatory for normal requests through `pair2idmap` and `id2name`.
- Directory attributes use a synthetic length of 1024 and NFS mode bits are derived from Plan 9 mode bits.
