# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/auth.c

Purpose: disabled/stubbed NFS authentication-file hooks.

Key behavior: `xfauth` returns nil; read/write/remove handlers log and return empty or failure results.

Integration notes: comments state NFS authentication is disabled. `nfsserver.c` still contains paths for root `#user` auth files, but this implementation makes those paths inert.
