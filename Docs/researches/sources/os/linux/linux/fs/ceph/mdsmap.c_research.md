# File Research: sources/os/linux/linux/fs/ceph/mdsmap.c

Implements decoding, selection, destruction, and availability checks for CephFS MDS maps.

Key behavior:
- `ceph_mdsmap_get_random_mds()` chooses a random ready MDS rank, preferring non-laggy ranks and falling back to laggy ready ranks if needed.
- Decodes only map fields the kernel client needs, while safely skipping or dropping many compatibility, metadata, failure, standby, balancer, and feature fields.
- Handles versioned MDS map and MDS info encodings, including address-vector decoding for newer info versions.
- Extracts epoch, client epoch, last failure, root, session timeout, session autoclose, max file size, max MDS, active rank count, data pools, CAS pool, fs name, damaged state, laggy count, and max xattr size.
- Computes `possible_max_rank` from active rank count, max MDS, and later the `in` set.
- Populates per-rank `ceph_mds_info` entries for valid ranks with positive state, global ID, address, laggy flag, and export target list.
- Validates decoded fs name against the mount namespace option for newer maps; older maps use `CEPH_OLD_FS_NAME`.
- Treats damaged maps, disabled maps, fully laggy active sets, or no active ranks as unavailable.
- Frees all export target arrays, data pool arrays, fs name, and the map itself in `ceph_mdsmap_destroy()`.

Important interactions:
- Used by `mds_client.c` when processing `CEPH_MSG_MDS_MAP`.
- Supplies MDS state, laggy-state, address, random-rank, and cluster-availability data for request routing and session recovery.
- Depends on Ceph messenger address decoding and mount namespace matching from Ceph common/super code.
