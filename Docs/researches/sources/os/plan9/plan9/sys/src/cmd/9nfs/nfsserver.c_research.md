# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/nfsserver.c

Purpose: NFS v2 server procedure implementation over a Plan 9 9P backend.

Key behavior: registers mount and NFS program maps, installs timer reload/stale-fid cleanup, and implements getattr, setattr, lookup, read, write, create, remove, rename, mkdir, rmdir, readdir, statfs, plus stubs for root/readlink/link/symlink/writecache. Operations decode NFS arguments, resolve `Xfid`s via `rpc2xfid`, perform 9P operations, translate errors/status, and serialize NFS replies.

Integration notes: relies on `nfs.c` for handle/fid/attribute conversion and on `9p.c` for actual 9P messages. Readdir converts Plan 9 stat records into NFS directory entries and tracks per-xfid offsets.
