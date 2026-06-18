<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/rgw.conf -->
## sources/user-network-fs/nfs-ganesha/src/config_samples/rgw.conf

Purpose: sample NFSv4 export of a Ceph RGW namespace through FSAL_RGW.

Important config surface: `EXPORT` id `1` exports `Path = "/"` at `Pseudo = "/"`, restricts `Protocols = 4` and `Transports = TCP`, and provides RGW user/access/secret key fields under `FSAL { Name = RGW; ... }`. The `MDCACHE` block warns that `Dir_Chunk` must not be set to `0`. The `RGW` block points to `ceph_conf`, client `name`, cluster, and optional `init_args`.

Control flow/state: Ganesha maps NFS operations onto RGW object/bucket semantics. Persistent state lives in Ceph/RGW. MDCACHE directory chunking influences POSIX-style `readdir` behavior over object storage.

Dependencies/integration: requires FSAL_RGW, Ceph libraries/configuration, valid RGW credentials, and network access to the Ceph cluster.

Risks: sample credentials are placeholders and must not be committed with real secrets. Exporting object storage as NFS has semantic gaps around directories, renames, permissions, and consistency. Setting `Dir_Chunk = 0` can break RGW `readdir`.

Test signals: validate config parsing with real Ceph settings, mount NFSv4 over TCP, list buckets/objects, and exercise create/read/remove while watching RGW and Ganesha logs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/rgw.conf -->
