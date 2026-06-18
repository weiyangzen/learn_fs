# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/portmapper.c

Purpose: minimal SunRPC portmapper service for 9nfs-related programs.

Key behavior: static map advertises NFS v2 and mount on UDP 2049, PCNFSD v1/v2 on UDP 1111. Implements null, set/unset, getport, dump, and callit. `set` always returns false; `unset` true; `callit` only responds for proc 0 with port and empty result.

Integration notes: runs on port 111 and uses shared RPC server/codec. It is static, not a general dynamic portmapper.
