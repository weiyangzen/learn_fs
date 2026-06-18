# File Research: sources/os/linux/linux-stable/fs/ceph/mds_client.c

## Purpose

`mds_client.c` is the CephFS kernel client's central Metadata Server control plane. It manages MDS sessions, request routing, request encoding/replay, reply parsing, capability renewal/release/reconnect, dentry leases, MDS map updates, fsmap handling, metric-session binding, MDS auth-cap checks, and mount sync/teardown behavior.

## Major Responsibilities

- Parses MDS replies, including versioned inode payloads, directory fragments, leases, readdir entries, create inode delegation, file-lock replies, vxattrs, snap blobs, fscrypt auth/file fields, alternate names, quotas, birth times, change attributes, and subvolume IDs.
- Tracks in-flight metadata requests in `mdsc->request_tree`, assigns tids, manages completion and safe-completion state, aborts timed-out or interrupted requests, and invalidates directory completeness/leases after aborted write namespace operations.
- Chooses an MDS using explicit resend hints, directory fragment authority/replicas, inode caps, or random active MDS fallback.
- Opens, closes, unregisters, reconnects, and periodically renews MDS sessions.
- Encodes session-open metadata including hostname, kernel version, entity id, mount root, supported CephFS feature bits, supported metric spec, flags, and `oldest_client_tid`.
- Builds metadata request messages with path encodings, cap/dentry releases, uid/gid and idmapped-mount handling, fscrypt auth/file data, fscrypt long-name alternate names, retry/forward counters, and optional pagelist payloads.
- Handles unsafe/safe reply sequencing. Unsafe replies populate client cache and mark requests unsafe; safe replies unregister requests and wake umount waiters.
- Handles request forwarding by resetting session state and resending to the forwarded MDS while guarding against retry/forward counter overflow.
- Reconnects after MDS restart by replaying unsafe requests, sending cap reconnect records, encoding file locks and snap realm state, supporting multi-message reconnect when needed.
- Maintains dentry leases by handling revoke/renew messages and sending lease messages back to MDS.
- Handles fsmap and mdsmap messages, updates subscriptions, swaps maps, checks rank state transitions, kicks waiting requests, closes stale sessions, opens export target sessions, and sends reconnects for recovering ranks.
- Provides `ceph_mdsc_sync`, pre-umount flushing, session close, forced unmount, initialization, destruction, and messenger connection callbacks.

## Key Data and Control Flow

- `parse_reply_info*()` decodes on-wire reply fragments into `struct ceph_mds_reply_info_parsed`; memory owned by parsed fscrypt fields and readdir buffers is released in `destroy_reply_info()`.
- `ceph_mdsc_create_request()` creates request objects; `ceph_mdsc_submit_request()` pins relevant caps, registers the request, and calls `__do_request()`.
- `__do_request()` performs mount-state checks, waits for initial maps when needed, chooses an MDS, opens/registers sessions, enforces feature requirements, queues requests behind unopened sessions, or sends them.
- `create_request_message()` is the main request serializer. It handles parent path construction, old-dentry path construction, release encoding, idmapped owner/caller ids, request head version compatibility, and fscrypt fields.
- `handle_reply()` validates session/tid, detects duplicate safe/unsafe replies, parses the reply, creates/gets target inodes, applies snap traces, fills inode/dentry cache, prepopulates readdir, stores reply state, completes waiters, and updates metadata metrics.
- `check_new_map()` compares old/new MDS maps and drives close/reconnect/kick behavior for changed, laggy, stopped, active, or export-target ranks.
- `send_mds_reconnect()` composes reconnect state by replaying requests, flushing caps, walking session caps, encoding snap realms, and sending `CEPH_MSG_CLIENT_RECONNECT`.

## Important Interactions

- Depends on `mds_client.h` for client/session/request data structures.
- Depends on `mdsmap.c/h` for rank state, addresses, laggy checks, map decode, and random MDS selection.
- Calls into caps, inode, dir, snap, super, crypto/fscrypt, messenger, monitor, and metric subsystems.
- Integrates with `quota.c` through `ceph_handle_quota()` dispatch and quotarealm cleanup during pre-umount.
- Integrates with `metric.c` by binding metric collection to sessions that advertise `CEPHFS_FEATURE_METRIC_COLLECT`.

## Concurrency and Lifetime Notes

- `mdsc->mutex` protects sessions, request tree, waiting lists, map swaps, and many high-level client transitions.
- `session->s_mutex` serializes session control processing and reconnect/close/cap-renew operations.
- `session->s_cap_lock`, inode `i_ceph_lock`, `cap_dirty_lock`, `cap_delay_lock`, `snap_rwsem`, dentry locks, and RCU are used for cap/session/inode/dentry/snap coordination.
- Request lifetime uses `kref`; session lifetime uses `refcount_t`.
- Safe teardown flushes messenger work before freeing structures that may still be referenced by dispatch/reply handlers.
- Reconnect code explicitly marks `s_cap_reconnect` so cap removal does not queue stale cap releases while reconnect state is being composed.

## Edge Cases and Compatibility

- Supports legacy and versioned reply/request encodings.
- Handles old MDSes that lack 32-bit retry/forward fields, owner uid/gid support, metric collection, subvolume metrics, or newer session operations.
- Guards retry and forward counter overflow with `-EMULTIHOP`.
- Handles async unlink conflict waits to avoid create/open races with delayed async unlink.
- Handles async create forwarding by moving auth caps between sessions when necessary.
- Has special fscrypt handling for long encrypted names and no-key readdir cases.
- Detects blocklisted sessions from metadata or flags and can trigger clean recovery.
- During sync, flushes dirty caps, cap releases, mdlog, unsafe write requests, and cap flush completions.

## Research Notes

This file is the operational hub for CephFS metadata correctness. The riskiest areas are request message serialization, replay semantics, lock ordering across `mdsc->mutex` and `session->s_mutex`, reconnect pagination, and cache filling after replies. Any changes here need tests or reasoning around MDS feature compatibility, interrupted requests, unsafe/safe reply ordering, and session-map transitions.
