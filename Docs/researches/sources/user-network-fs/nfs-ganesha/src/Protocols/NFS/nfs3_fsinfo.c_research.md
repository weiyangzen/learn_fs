## sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_fsinfo.c

Purpose: implements NFSv3 `FSINFO`.

APIs and flow: `nfs3_fsinfo` converts the root handle, calls `fsal_statfs` for time delta, fills read/write/readdir preferences from export atomics, gets max file size from FSAL export ops, sets static property flags for links/symlinks/homogeneous/cansettime, attaches post-op attrs, and returns `NFS3_OK`.

State/dependencies: read-only over export configuration and FSAL filesystem info. Depends on atomics in `gsh_export`, FSAL statfs/maxfilesize, and post-op attr helpers.

Risks/tests: there is a likely typo on statfs failure assigning `res_fsstat3.status` instead of `res_fsinfo3.status`. Test FSAL statfs failure, export preference values, maxfilesize propagation, property flags, stale handles, and post-op attrs.
