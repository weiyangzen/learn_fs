# File Research: sources/os/linux/linux/fs/ceph/mds_client.h

Defines the CephFS MDS client’s public internal contract: feature bits, reply parse structures, session state, request state, quota helpers, path info, and MDS client-global state.

Key behavior:
- Defines CephFS feature IDs supported by the kernel client, including reply encoding, lazy cap wanted, multi reconnect, delegated inode numbers, metric collection, alternate names, vxattr op, 32-bit retry/forward counters, owner uid/gid, MDS auth caps, and subvolume metrics.
- Documents core lock ordering used by the MDS client and cap/snap paths.
- Defines MDS auth-cap match structures for uid/gid/path/fs-name/root-squash matching and readable/writeable permissions.
- Defines parsed reply structures for inode data, directory entries, xattrs, file locks, readdir extras, create inode results, and snap blobs.
- Defines `CEPH_CAPS_PER_RELEASE`, accounting for cap release message header and trailing OSD epoch barrier.
- Defines MDS session states and `struct ceph_mds_session`, including connection, auth handshake, cap lists, cap release work, dirty/flushing cap lists, renewal state, waiting/unsafe requests, and delegated inode xarray.
- Defines MDS selection modes: any, random, or authoritative.
- Defines `struct ceph_mds_request`, including request target objects, paths, parent/old dentry information, flags, request args, fscrypt fields, credentials/idmap, drop/release caps, wire messages, reply parse state, completions, unsafe tracking, retry/forward state, delegated ino, and cap reservation.
- Defines `struct ceph_mds_client`, the global MDS client state: map, sessions, request tree, snap realms, quota realm cache, cap pools, delayed work, metrics, subvolume metrics, pool permissions, auth caps, and nodename.
- Provides prototypes for request lifecycle, session iteration, cap release/reclaim work, sync/umount paths, mdsmap/fsmap handling, leases, delegated inode handling, access checks, and path building/freeing.
- Provides inline request ref helpers, async-create wait helper, and `ceph_mdsc_free_path_info()`.

Important interactions:
- Included by most CephFS source files that touch metadata operations, sessions, caps, quotas, metrics, or MDS maps.
- Bridges `mds_client.c` with `mdsmap.h`, `metric.h`, `subvolume_metrics.h`, and `super.h`.
- The structs here are the shared memory layout for MDS reply parsing and request construction.
