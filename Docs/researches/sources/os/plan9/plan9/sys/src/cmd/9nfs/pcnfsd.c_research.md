# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/pcnfsd.c

Purpose: PC-NFS daemon RPC service.

Key behavior: registers PCNFSD v1/v2 program maps, initializes facilities and uid maps, implements null, info, v1 auth, and v2 auth. Auth requests descramble ID/password fields but do not validate passwords; they map username to uid/gid or fall back to uid 1 and return canned home/comment data.

Integration notes: listens on port 1111 via shared `server`. Intended compatibility service, not strong authentication.
