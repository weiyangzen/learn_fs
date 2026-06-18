# File Research: sources/os/plan9/plan9/sys/src/cmd/vac/vacfs.c

Purpose: serve a Vac archive as a 9P filesystem.

Command behavior:
- Supports debug tracing, cache size, stdio mode, Venti host, service registration, mountpoint, no-permission mode, and Venti verbosity.
- Opens the Vac archive read-only and serves 9P requests over stdio, `/srv`, or a mounted pipe.

Core structures and dispatch:
- `Fid` tracks 9P fid state: busy/open flags, user, qid, associated `VacFile`, and active directory enumerator.
- `initfcalls` maps 9P request types to handler functions.
- `io` reads 9P messages, dispatches by `rhdr.type`, builds replies, and writes responses.

Handlers:
- `rversion`, `rauth`, and `rattach` implement session setup without authentication.
- `rwalk` clones/walks fids through Vac directories using `vacfilewalk`.
- `ropen` enforces permission checks and read-only constraints.
- `rread` reads file data or directory records through `vacdirread`.
- `rstat` converts `VacDir` to 9P `Dir` with `vacstat`.
- `rwrite` and `rwstat` always return read-only.
- `rcreate` and `rremove` contain vestigial mutation paths, but the filesystem is opened read-only in `threadmain`.

Integration points:
- Uses `vac.h` APIs, Plan 9 `fcall.h`, and 9P conversion functions.
- `vacstat` maps Vac mode bits to Plan 9 qid/type/mode bits and applies qidspace offsets.

Risks:
- `rremove` appears to invert `vacfileremove` success handling: it records an error when `vacfileremove` returns `0`. This path is effectively unreachable for the read-only mount but is risky if write support is revived.
- `rcreate` checks `fs->mode & ModeSnapshot`, but `fs->mode` is a Venti open mode, not Vac mode bits; actual read-only protection comes later from `vacfilecreate`.
- Permission checks compare user to `uid` or `gid` strings only; there is no group database lookup.
