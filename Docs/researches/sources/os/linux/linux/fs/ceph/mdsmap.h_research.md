# File Research: sources/os/linux/linux/fs/ceph/mdsmap.h

Declares the reduced CephFS MDS map representation used by the kernel client.

Key behavior:
- Defines `struct ceph_mds_info` with global ID, entity address, state, export target count/list, and laggy flag.
- Defines `struct ceph_mdsmap` with epochs, root, session timeouts, max file/xattr sizes, max/active/possible ranks, per-rank info, data pools, CAS pool, enabled/damaged/laggy state, and fs name.
- Provides inline helpers:
  - `ceph_mdsmap_get_addr()` returns a rank address or NULL if out of range.
  - `ceph_mdsmap_get_state()` returns rank state or `CEPH_MDS_STATE_DNE` if out of range.
  - `ceph_mdsmap_is_laggy()` checks rank laggy state.
- Declares random MDS selection, decoding, destruction, and cluster-availability helpers.

Important interactions:
- Shared by `mds_client.c` and `mdsmap.c`.
- Keeps the kernel-side map intentionally smaller than the full on-wire MDS map by storing only client-relevant fields.
