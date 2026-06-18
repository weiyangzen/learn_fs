<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/rgw_bucket.conf -->
## sources/user-network-fs/nfs-ganesha/src/config_samples/rgw_bucket.conf

Purpose: sample FSAL_RGW export scoped to a single bucket.

Important config surface: `EXPORT` id `1` uses `Path = "testbucket"` and `Pseudo = "/testbucket"`, allows RW NFSv4 over TCP, and supplies RGW user/access/secret keys. The `RGW` block selects `ceph_conf`, client `name`, and `cluster`.

Control flow/state: NFS clients see the named bucket as the export root; operations are translated to RGW object operations. Persistent state is external in Ceph RGW.

Dependencies/integration: requires FSAL_RGW, a live Ceph cluster, valid RGW user credentials with bucket access, and the bucket named in `Path`.

Risks: real credentials must be protected. Bucket-level export narrows namespace exposure but still has object-storage semantic differences from POSIX. Missing bucket or wrong user permissions result in mount or operation failures that look like NFS errors to clients.

Test signals: mount `/testbucket` over NFSv4, verify object listing and object I/O, and test permission failures with invalid credentials to ensure errors are diagnosable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/rgw_bucket.conf -->
