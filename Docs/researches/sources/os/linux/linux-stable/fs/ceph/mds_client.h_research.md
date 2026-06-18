# File Research: sources/os/linux/linux-stable/fs/ceph/mds_client.h

## Purpose

`mds_client.h` defines the CephFS MDS client interface, feature negotiation constants, reply parse containers, session state, request state, quota realm tracking, snap/pool/cap client state, and public functions used by the rest of the CephFS kernel client.

## Major Definitions

- `enum ceph_feature_type` lists CephFS session feature bits such as reply encoding, lazy cap wanted, multi reconnect, delegated inode numbers, metric collection, alternate names, vxattr op support, 32-bit retry/forward counters, owner uid/gid, MDS auth-cap checks, and subvolume metrics.
- `CEPHFS_FEATURES_CLIENT_SUPPORTED` defines the client-advertised feature set.
- `struct ceph_mds_cap_match` and `struct ceph_mds_cap_auth` model path/fs/uid/gid/root-squash based MDS auth-cap rules.
- `struct ceph_mds_reply_info_in`, `struct ceph_mds_reply_dir_entry`, and `struct ceph_mds_reply_info_parsed` hold decoded MDS reply data, mostly as pointers into message buffers plus separately allocated fscrypt fields.
- `CEPH_CAPS_PER_RELEASE` calculates cap release batching capacity per page-sized message.
- MDS session states define lifecycle from `NEW` through `OPEN`, `HUNG`, `RESTARTING`, `RECONNECTING`, `CLOSING`, `CLOSED`, and `REJECTED`.
- `struct ceph_mds_session` stores per-rank connection, auth, caps, waiting/unsafe request lists, delegated inode xarray, sequence/feature/ttl state, and cap release work.
- `struct ceph_mds_request` stores request identity, operands, dentries/inodes/paths, cap releases, request/reply messages, parsed reply info, completions, retry/forward state, fscrypt fields, idmap, credentials, and unsafe tracking.
- `struct ceph_mds_client` stores global MDS client state: current mdsmap, sessions, request tree, snap realms, caps, delayed work, dentry leases, metrics, subvolume metrics, snapid map, pool permissions, quotarealm inode cache, auth caps, and shutdown state.
- `struct ceph_path_info` groups path string, length, base vino, and allocation ownership for path builders.

## Exported API Surface

- Session management: lookup/get/put session, session state name, iterate sessions, open export target session.
- Client lifecycle: `ceph_mdsc_init`, `ceph_mdsc_destroy`, close sessions, force umount, pre-umount, sync.
- Request lifecycle: create, submit, wait, do request, release request, invalidate aborted directory request.
- Cap/session helpers: queue cap release, flush session releases, trim caps, reclaim caps, queue unlink work, iterate session caps.
- Lease and path helpers: build paths, free path info, drop dentry lease, send lease message.
- Map handlers: handle MDS map and FS map.
- Quota/async helpers: wait on async create, wait on conflict unlink, delegated inode get/restore.
- Auth access: `ceph_mds_check_access`.

## Concurrency Notes

The header documents key lock ordering expectations: `session->s_mutex` above `mdsc->mutex`, `mdsc->snap_rwsem`, and inode `i_ceph_lock`, with lower locks for snap flush and cap delay. The structs mirror this by separating mutex-protected request/session topology from spinlock-protected cap, dentry lease, snap, and counter lists.

## Research Notes

This header is the contract for the MDS client subsystem. Its structs are large because request/session state spans VFS objects, Ceph wire protocol compatibility, cap lifetime, snap realms, fscrypt, idmapped mounts, and delayed asynchronous work. Changes to field ownership or lock protection here would have broad impact across MDS request handling, caps, quota, metrics, and unmount/reconnect paths.
