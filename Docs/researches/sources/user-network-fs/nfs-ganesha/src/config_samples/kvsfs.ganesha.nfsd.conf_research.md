<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/kvsfs.ganesha.nfsd.conf -->
## sources/user-network-fs/nfs-ganesha/src/config_samples/kvsfs.ganesha.nfsd.conf

Purpose: minimal NFS-Ganesha export sample for the KVSFS FSAL.

Important config surface: one `EXPORT` with `Export_Id = 77`, `Path = "/"`, `Pseudo = /kvsfs`, `Protocols = NFSV3, 4, 9p`, `SecType = sys`, `MaxRead`/`MaxWrite` set to 32768, `Filesystem_id = 192.168`, and a wildcard `client` allowing RW with `no_root_squash`. The `FSAL` block selects `name = KVSFS` and points `kvsns_config` at `/etc/kvsns.d/kvsns.ini`.

Control flow/state: declarative sample only. At daemon load, Ganesha parses the export, initializes the KVSFS FSAL, and uses the external KVS namespace config as persistent backend configuration.

Dependencies/integration: requires a build with KVSFS support, a valid KVS namespace configuration file, and consumers using NFSv3, NFSv4, or 9P. The wildcard client block integrates with Ganesha export access checks.

Risks: permissive wildcard RW/no-root-squash access is unsafe outside a controlled test network. The sample uses a fixed export id and filesystem id, which can collide in multi-export deployments. KVSFS startup will fail or behave incorrectly if `kvsns_config` is missing or stale.

Test signals: run `ganesha.nfsd` with the sample after installing KVSFS prerequisites, mount `/kvsfs`, and verify read/write behavior and protocol negotiation for NFSv3/NFSv4/9P where enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/kvsfs.ganesha.nfsd.conf -->
