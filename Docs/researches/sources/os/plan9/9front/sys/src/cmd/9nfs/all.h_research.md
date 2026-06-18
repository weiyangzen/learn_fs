# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/all.h

This is the umbrella include header for `9nfs`.

Key content:
- Includes Plan 9 system/library headers: `u.h`, `libc.h`, `ip.h`, `bio.h`, `auth.h`, `authsrv.h`, `fcall.h`, and `regexp.h`.
- Includes local headers: `dat.h`, `fns.h`, `rpc.h`, and `nfs.h`.
- Installs vararg format checks for `chat`, `clog`, `panic`, and `%I`.

Important interactions:
- Included by most `9nfs` C files.
- Centralizes subsystem type and function visibility.

Research notes:
- This header establishes that `9nfs` combines RPC, NFS, 9P, auth, and UID-map functionality.
