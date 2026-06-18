# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/main.c

Implements the Plan 9 9P filesystem front end for a remote CIFS/SMB server. It mounts remote shares and synthetic info files into a namespace, handling attach, walk, stat, open/create, read/write, remove, wstat, fid cloning/destruction, and server shutdown.

`Aux` tracks per-fid state: current path, share pointer, directory search handle/resume state, file handle, cached directory entries, cache bounds/expiry, and synthetic mtime override for open files. `Openfiles` is a circular list used for diagnostics and coordinated close/remove behavior.

Path walking integrates root info files, top-level shares, case validation, DFS share/path remapping, Trans2 metadata queries, and DFS reparse-point redirection. Directory reads use `T2findfirst/T2findnext`, cache batches briefly, remove `.`/`..`, and convert `FInfo` into Plan 9 `Dir`.

File open/create supports both classic SMB open/create and NT create paths depending on server capabilities. Reads and writes are chunked by negotiated MTU. Wstat implements rename, length changes, mtime/atime update, readonly attribute handling, and flushes open files for Win95-style metadata cache issues.

`main` handles CLI flags, dials with NetBIOS called-name discovery fallbacks, negotiates protocol, authenticates via factotum/auth helpers, connects `IPC$`, enumerates or connects requested shares, starts a keepalive process, and calls `postmountsrv`.

Important dependencies: almost every CIFS subsystem: `cifsdial`, `CIFSnegotiate`, `CIFSsession`, `CIFStreeconnect`, `RAPshareenum`, Trans2 metadata/directory operations, DFS mapping, SID update, packet auth, and Plan 9 lib9p.

Behavioral notes: the implementation is explicitly tuned for Windows/Samba SMB1 quirks, uses global session/share state, and exposes administrative/server information as ordinary readable files at the mount root.
