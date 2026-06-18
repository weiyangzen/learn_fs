# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_fha_new.h

Small kernel header for the newer NFS server FHA personality. It defines `FHANEW_SERVER_NAME` as `"nfsd"` and declares `fhanew_assign()` for assigning RPC requests to FHA-selected service threads.

This header is consumed by the NFS server krpc setup so the service pool can use the NFS-specific file-handle affinity callback.
