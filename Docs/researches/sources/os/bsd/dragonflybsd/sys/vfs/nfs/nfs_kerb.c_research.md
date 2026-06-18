# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_kerb.c

This file contains the NFS client helper daemon path used for legacy Kerberos/NQNFS authorization support. It is compiled only when server-side NFS support is not disabled by `NFS_NOSERVER`.

Primary entry point:
- `nfs_clientd()` coordinates authorization-string handoff between userland `nfssvc` activity and an `nfsmount`.
- It consumes `NFSSVC_GOTAUTH` input, validates supplied auth/verifier lengths against mount buffers, copies auth material from user space, stores auth type and optional Kerberos key, then marks `NFSSTA_HASAUTH` or `NFSSTA_AUTHERR`.
- If auth is needed but not available, it sets `NFSSTA_WAITAUTH`, copies an `nfsd_cargs` request back to userland, and returns `ENEEDAUTH`.
- The daemon sleeps on mount auth state and unmounts on interrupt/restart signals.

Lifecycle and cleanup:
- The loop exits when `NFSSTA_DISMNT` is set.
- On teardown, all `nfsuid` cache entries are removed from the mount’s hash/LRU lists and freed.
- Finally `nfs_free_mount()` releases the mount structure.

Important interactions:
- Uses `nm_state` flags such as `NFSSTA_WAITAUTH`, `NFSSTA_HASAUTH`, `NFSSTA_AUTHERR`, and `NFSSTA_DISMNT`.
- Wakes sleepers on `nm_authlen` after auth completion.
- Depends on `nfs_socket.c` and `nfs_subs.c` Kerberos paths that request or validate auth and nickname credentials.

Caveats:
- The file is narrowly scoped and retains legacy Kerberos behavior; real crypto sections elsewhere are guarded or stubbed by `NFSKERB`.
- State transitions rely on mount flags and sleeps rather than an explicit state-machine type.
