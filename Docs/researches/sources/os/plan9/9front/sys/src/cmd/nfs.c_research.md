# File Research: sources/os/plan9/9front/sys/src/cmd/nfs.c

A 9P file server backed by NFSv3 and MOUNT RPC.

Key elements:
- Wraps portmapper, MOUNT v3, and NFS v3 RPCs with helpers for null, mount, getattr, access, mkdir, create, read, write, remove, rmdir, rename, setattr, commit, lookup, and readdir/readdirplus.
- Maps Plan 9 fids to `FidAux`, storing NFS file handle, parent handle, name, readdir cookie, error buffer, and AuthSys credentials.
- Reads passwd/group files into a `Map`, supports name/id lookups, and precomputes SunAuthUnix credential blobs.
- `fsattach` mounts an export path and initializes root fid state.
- `fsopen`, `fscreate`, `fsread`, `fswrite`, `fsremove`, `fsstat`, `fswstat`, and `fswalk` translate 9P operations into NFSv3 RPCs.
- Directory reads prefer READDIRPLUS and fall back to READDIR if unsupported.
- Uses a channel/thread dispatch model so each 9P request is handled in a worker thread.
- `threadmain` can query portmapper for mount/NFS ports or accept explicit mount and NFS addresses.

Notable behavior:
- Plan 9 permissions for created files are masked using the parent directory mode, and group is inherited.
- `wstat` may rename first and then setattr, explicitly noting loss of atomicity if setattr fails.
- `fsflush` forwards flush tags to both RPC clients.
- Service is posted with `threadpostmountsrv`, and `/srv/<srvname>` permissions can be adjusted with `-p`.

Risks and quirks:
- Remove/rename depend on stored parent handle and name, described as a “botch” in comments.
- `readplus` is a global tri-state controlling READDIRPLUS fallback.
- User/group maps are optional; missing users fall back to nobody-style credentials.
