# File Research: sources/os/bsd/openbsd-src/sbin/mount_nfs/mount_nfs.c

`mount_nfs.c` implements NFS mount negotiation and the final `mount(MOUNT_NFS, ...)` call. It supports NFSv2/v3 selection, UDP/TCP transport, background retries, soft/intr/noconn/dumbtimer/rdirplus/reserved-port behavior, size/time/retrans/readahead/cache tuning, max group count, and shared mount options.

`getnfsargs()` parses `host:path` and `path@host` specs, resolves IPv4 host addresses, queries portmap for the NFS port, contacts the remote mount daemon over TCP or UDP, obtains the file handle through RPC, falls back from NFSv3 to v2 on version mismatch unless forced, and supports background retry by forking and detaching.

The file contains XDR helpers for mount path and file-handle replies. For NFSv3, it validates file-handle size and checks the server’s auth list for `RPCAUTH_UNIX`, accepting an empty list as Unix auth for compatibility.

Important coupling: uses SunRPC client APIs, portmap, NFS kernel argument structures, and shared mount-option parsing.
