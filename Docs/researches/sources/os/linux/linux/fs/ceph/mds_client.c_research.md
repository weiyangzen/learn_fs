# File Research: sources/os/linux/linux/fs/ceph/mds_client.c

Implements the CephFS kernel client’s Metadata Server client: MDS sessions, metadata requests, replies, reconnect/replay, leases, caps renewal/release, MDS map handling, and messenger connection callbacks.

Key behavior:
- Parses MDS replies for inode traces, directory fragments, leases, readdir entries, file locks, create delegated inode numbers, vxattr values, snap blobs, quotas, pool namespaces, fscrypt metadata, subvolume IDs, and versioned encodings.
- Maintains per-MDS sessions with states from new/opening/open/hung/restarting/reconnecting/closing/closed/rejected.
- Registers sessions lazily, opens them with client metadata, supported CephFS feature bits, metric specs, and oldest client TID.
- Chooses target MDS ranks using resend hints, directory frag hashes, auth caps, replica distribution, laggy-state filtering, or random active MDS fallback.
- Tracks in-flight MDS requests in an rb-tree keyed by TID, assigns credentials/idmap context, reserves caps, and links unsafe directory operations for fsync/safe-reply tracking.
- Builds wire requests with path encoding, snap path bases, fscrypt alternate names, cap/dentry release records, gid lists, fscrypt auth/file fields, replay flags, retry/forward counters, async flags, and idmapped owner UID/GID fields when supported.
- Handles synchronous request submission/wait as well as aborts on timeout, signal, shutdown, fenced I/O, unavailable maps, unsupported MDS features, or rejected sessions.
- Handles unsafe and safe replies separately: unsafe replies fill caches and complete the caller, while safe replies unregister the request and complete safe waiters.
- Processes reply traces through `ceph_fill_trace()` and readdir results through `ceph_readdir_prepopulate()`, with snap trace updates serialized by `snap_rwsem`.
- Handles request forwarding by updating resend MDS and forward sequence, while detecting overflow/multihop loops.
- Sends periodic cap renewal, keepalive, cap release, flushmsg ack, and mdlog flush messages.
- Batches cap releases into `CEPH_MSG_CLIENT_CAPRELEASE` messages with an OSD epoch barrier.
- Trims caps on MDS recall by dropping unused caps or pruning aliases/dentries under memory pressure.
- Replays unsafe requests and old requests during MDS reconnect, and sends reconnect payloads containing caps, paths, locks, snaprealm information, and snap-follow sequence data.
- Supports delegated inode numbers on 64-bit builds via an xarray, while 32-bit builds ignore delegated ranges.
- Reacts to MDS map changes by closing removed sessions, reconnecting restarted sessions, kicking requests when ranks become active, opening export target sessions, and handling laggy ranks.
- Handles session control messages, including open, renewcaps, close, stale, recall-state, flushmsg, force-readonly, reject, blocklist detection, MDS auth caps, metrics enablement, and subvolume metrics enablement.
- Handles dentry lease revoke/renew messages and sends lease revoke acknowledgements.
- Handles FS map selection for named CephFS mounts and MDS map decoding/swapping.
- Provides mount sync, pre-umount, force-umount, close-session, and destroy paths that flush dirty caps, wait for unsafe metadata operations, clean quota realm inodes, and tear down sessions.
- Implements local MDS auth-cap access checks by matching current credentials, fs name, mount path, auth path, readable/writeable bits, and root-squash policy.
- Provides messenger connection operations for dispatch, allocation, peer reset, session refcounting, auth handshake, authorizer invalidation, message signing, and signature verification.

Important interactions:
- Central coordinator for `caps.c`, `dir.c`, `inode.c`, `snap.c`, `quota.c`, `metric.c`, `mdsmap.c`, `crypto.c`, and the Ceph messenger/auth layers.
- Uses `struct ceph_mds_client`, `struct ceph_mds_session`, and `struct ceph_mds_request` from `mds_client.h`.
- Uses `ceph_mdsmap_decode()` and map helper state from `mdsmap.c`.
- Updates metadata latency through `ceph_update_metadata_metrics()` and binds metric collection sessions when MDS supports metric collection.
- Dispatches quota messages to `ceph_handle_quota()`.
- Relies on careful lock ordering among `session->s_mutex`, `mdsc->mutex`, `snap_rwsem`, inode cap locks, cap dirty locks, and dentry locks.
