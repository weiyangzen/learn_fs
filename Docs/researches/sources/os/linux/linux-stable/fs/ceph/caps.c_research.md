# File Research: sources/os/linux/linux-stable/fs/ceph/caps.c

## Purpose

`caps.c` implements CephFS client capability management. Capabilities are MDS-issued permissions that authorize cached inode metadata, cached file data, writes to OSDs, directory operations, and dirty metadata updates. This file owns cap allocation, acquisition, release, revocation, dirty flushing, snap flushing, MDS cap message handling, reconnect/import/export handling, and open-mode wanted-cap tracking.

## Main Responsibilities

- Maintain per-MDS-session `ceph_cap` objects and per-inode cap rb-trees.
- Decide which caps are issued, implemented, wanted, used, dirty, flushing, or revoking.
- Acquire cap references for reads, writes, cache use, lazy I/O, mmap, and sync operations.
- Flush dirty inode metadata and capsnaps to the MDS.
- Respond to MDS `GRANT`, `REVOKE`, `TRUNC`, `EXPORT`, `IMPORT`, `FLUSH_ACK`, and `FLUSHSNAP_ACK` messages.
- Queue delayed cap release and cap dirty work.
- Encode cap and dentry releases into outgoing MDS requests.
- Handle cap purging during shutdown/session loss.

## Capability State Model

Important state categories:
- `issued`: caps currently granted by the MDS.
- `implemented`: caps the client still effectively holds, including revoking caps not yet acknowledged.
- `wanted`: caps the client asks the MDS to keep or grant.
- `used`: caps pinned by active refs such as read, write, cache, buffer, pin, or exclusive refs.
- `dirty`: metadata cap bits modified locally and not yet flushed.
- `flushing`: dirty cap bits sent to MDS but not yet acknowledged.

`ceph_cap_string()` formats these bitsets for debug logs.

## Allocation and Reservation

- `ceph_caps_init()` and `ceph_caps_finalize()` manage the global cap free list.
- `ceph_reserve_caps()`, `ceph_unreserve_caps()`, `ceph_get_cap()`, and `ceph_put_cap()` maintain total, used, reserved, and available cap counters.
- Reservation can trigger `ceph_trim_caps()` on sessions before failing allocation.
- The code keeps a minimum cap pool to reduce allocation churn.

## Per-Inode Cap Management

- `__get_cap_for_mds()` looks up a cap by MDS id in the inode rb-tree.
- `ceph_add_cap()` creates or updates a cap, links it into the session list, updates auth cap state, snap realm, wanted bits, and issue sequences.
- `__ceph_remove_cap()` removes a cap from inode/session structures and optionally queues a release to the MDS.
- `change_auth_cap_ses()` moves dirty/flushing inode list entries when the auth MDS changes.

## Cap Wanted and Used Logic

- `__ceph_caps_used()` derives cap bits from active reference counters and page-cache state.
- `__ceph_caps_file_wanted()` derives wanted caps from open file modes and recent read/write access.
- `__ceph_caps_wanted()` combines open-mode wanted caps with used caps, adding exclusive caps when needed.
- `__ceph_caps_mds_wanted()` reports what has already been requested from MDS sessions.

Open-mode counters are maintained by `ceph_get_fmode()`, `ceph_put_fmode()`, and `__ceph_touch_fmode()`.

## Cap Acquisition

The core acquisition path is:
- `ceph_try_get_caps()` for nonblocking read/cache cap attempts.
- `ceph_get_caps()` and `__ceph_get_caps()` for blocking acquisition by file operations.
- `try_get_cap_refs()` checks issued caps, revoking caps, max-size limits, pending capsnaps, file-lock errors, readonly sessions, shutdown state, and wanted-cap consistency.
- `check_max_size()` requests larger write max-size from the MDS when writes exceed current authorization.

Special return conditions:
- `-EAGAIN`: nonblocking path would need to sleep.
- `-EFBIG`: write exceeds current max size and should request expansion.
- `-EUCLEAN`: caps may need renewal after session disruption.

## Dirty Metadata and Flushes

- `__ceph_mark_dirty_caps()` marks inode metadata caps dirty, allocates/prepares a cap flush object, queues inode on session dirty list, and marks the VFS inode dirty as needed.
- `try_flush_caps()` sends immediate dirty cap flushes and returns flush tid.
- `ceph_write_inode()` flushes dirty caps for writeback or queues immediate cap work.
- `ceph_fsync()` waits for file data, dirty metadata cap flushes, and unsafe MDS operations when required.

Flush ordering is tracked with monotonic `last_cap_flush_tid`, global `cap_flush_list`, and per-inode `i_cap_flush_list`.

## Snapshot Cap Handling

Snapshot metadata is represented by `ceph_cap_snap`:
- `__ceph_flush_snaps()` sends eligible capsnap flushes in order after dirty pages and sync writes finish.
- `ceph_flush_snaps()` resolves the auth session and removes the inode from the snap flush queue.
- `ceph_try_drop_cap_snap()` discards capsnaps that do not need MDS flushes.
- `ceph_put_wrbuffer_cap_refs()` decrements dirty page refs for either head snap context or matching capsnap context and triggers snap flush when complete.
- `handle_cap_flushsnap_ack()` removes acknowledged capsnaps.

This cooperates directly with `addr.c` writeback snap-context ordering.

## Cap Reconciliation

`ceph_check_caps()` is the central reconciliation loop. It:
- Computes file-wanted, used, dirty, flushing, issued, implemented, revoking, want, and retain sets.
- Tries nonblocking page-cache invalidation when cache/lazy caps are revoked and no dirty buffers remain.
- Sends cap updates, flushes, revocation acknowledgments, wanted-cap changes, and max-size updates.
- Queues writeback when FILE_BUFFER revocation is blocked by dirty pages.
- Queues async invalidation when immediate invalidation fails.
- Handles pending cap flush and capsnap flush ordering before normal cap messages.

## MDS Message Encoding

- `cap_msg_args` is the in-memory form for outgoing cap messages.
- `encode_cap_msg()` serializes cap update/flush/flushsnap messages, including timestamps, ownership, mode, xattrs, inline-data marker, epoch barrier, oldest flush tid, btime, change attr, advisory flags, dirstats placeholders, and fscrypt fields.
- `__send_cap()` allocates and sends `CEPH_MSG_CLIENT_CAPS`.
- `__send_flush_snap()` sends `CEPH_CAP_OP_FLUSHSNAP`.

## Incoming MDS Cap Messages

`ceph_handle_caps()` decodes `CEPH_MSG_CLIENT_CAPS`, parses versioned payload fields, locates the inode, and dispatches by op:
- `handle_cap_grant()` handles grants and revocations, updates metadata fields, layout, xattrs, dirstats, inline data, max size, truncation state, and queues writeback/invalidation when needed.
- `handle_cap_flush_ack()` clears acknowledged flushing caps and releases flush records.
- `handle_cap_flushsnap_ack()` removes flushed capsnaps.
- `handle_cap_trunc()` applies MDS truncation state.
- `handle_cap_export()` and `handle_cap_import()` migrate caps between MDS sessions.

If the client lacks the inode or cap for a grant/revoke/import, it queues an explicit cap release back to the MDS.

## Reconnect, Session Loss, and Purge Behavior

- `ceph_early_kick_flushing_caps()`, `ceph_kick_flushing_caps()`, and `ceph_kick_flushing_inode_caps()` resend or mark flushing cap messages after revocation/reconnect conditions.
- `ceph_purge_inode_cap()` removes caps during shutdown/session loss, drops dirty/flushing state with mapping errors, marks file locks erroneous, removes capsnaps, and requests page invalidation when needed.
- `remove_capsnaps()` removes all capsnaps and wakes inode/global flush waiters.

## Release Encoding

- `ceph_encode_inode_release()` encodes inode cap release records into outgoing MDS request buffers, dropping only unused clean caps.
- `ceph_encode_dentry_release()` additionally encodes dentry lease release information and encrypts dentry names when needed.
- `ceph_drop_caps_for_unlink()` aggressively drops link caps and queues dirty cap flushes for soon-unlinked files.

## Important Dependencies

- `addr.c`: dirty page writeback, wrbuffer ref release, page-cache invalidation/writeback queues.
- `crypto.c`/`crypto.h`: fscrypt auth fields, encrypted names in dentry release, encrypted file size handling.
- MDS client/session structures and message transport.
- Linux inode writeback, fscrypt, file locking, wait queues, rb-trees, and list APIs.

## Edge Cases and Risks

- The file is concurrency-heavy: most inode cap state is protected by `i_ceph_lock`, while session lists use `s_cap_lock`, dirty/flush lists use `cap_dirty_lock`, and snap state uses `snap_rwsem`.
- Cap revocation cannot be acknowledged until conflicting active refs or dirty page writeback complete.
- Dirty cap flush ordering is maintained by flush tids; wake propagation moves wait responsibility to preceding flush records when removing later records.
- Auth MDS migration requires careful sequence/migrate-sequence checks to avoid dropping valid caps.
- Encrypted files report rounded traditional size in cap messages while carrying real size in fscrypt-specific fields.
