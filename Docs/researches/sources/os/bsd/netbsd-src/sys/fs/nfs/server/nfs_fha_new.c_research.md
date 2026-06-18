# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_fha_new.c

Implements the NFS server File Handle Affinity personality for the newer NFS server. It initializes `fha_params`, installs callback functions, creates the `vfs.nfsd.fha` sysctl subtree, and delegates scheduling decisions to the common FHA framework.

Callbacks translate NFSv2 procedure numbers to generic NFSv3-style procedure numbers, realign mbufs, extract a compact hash from an NFS file handle, classify reads and writes, parse read/write offsets, identify procedures without offsets, and select shared or exclusive lock types per NFS procedure. `fhanew_assign()` is the exported hook used by the RPC service pool to choose a service thread.

The file depends on common NFS RPC parsing macros, `newnfs_nfsv3_procid[]`, `newnfs_realign()`, `fha_init()`, `fha_uninit()`, `fha_assign()`, and `fhe_stats_sysctl()`. Its file-handle hash intentionally reduces a variable-size handle to a 64-bit xor-style value for scheduling affinity, not for security or identity.
