# File Research: sources/os/linux/linux-stable/fs/ceph/mdsmap.h

## Purpose

`mdsmap.h` defines the in-memory MDS map structures and helper functions used by the CephFS MDS client.

## Major Definitions

- `struct ceph_mds_info` stores per-rank global id, network address, state, laggy flag, export target count, and export target rank array.
- `struct ceph_mdsmap` stores map epochs, root rank, session timeout/autoclose values, maximum file size, maximum xattr size, max/active rank counts, possible rank range, rank info array, data pools, CAS pool, enabled/damaged state, laggy count, and filesystem name.
- `ceph_mdsmap_get_addr()` returns the rank address or `NULL` if rank is out of range.
- `ceph_mdsmap_get_state()` returns `CEPH_MDS_STATE_DNE` for out-of-range ranks and asserts against negative ranks.
- `ceph_mdsmap_is_laggy()` returns laggy status only for valid ranks.

## Exported API

- `ceph_mdsmap_get_random_mds()`
- `ceph_mdsmap_decode()`
- `ceph_mdsmap_destroy()`
- `ceph_mdsmap_is_cluster_available()`

## Research Notes

This is a compact data contract for `mdsmap.c` and `mds_client.c`. Its fields are only the subset of the full Ceph MDS map that the kernel client needs for routing, recovery, feature limits, and mount availability decisions.
