# File Research: sources/os/linux/linux/fs/ceph/caps.c

## Purpose
Implements CephFS client capability management. Capabilities are MDS-issued permissions that allow cached inode metadata/data access, buffered writes to OSDs, directory caching, metadata mutation, and delayed release. This file owns the cap state machine for reservation, issuance, revocation, dirty metadata flushing, cap snapshots, MDS migration, cap refs, fsync/writeback synchronization, and release encoding.

## Main Responsibilities
- Maintains per-MDS-session and per-inode capability state.
- Allocates, reserves, reuses, and trims `struct ceph_cap` objects.
- Tracks issued, implemented, wanted, used, dirty, and flushing cap masks.
- Sends cap update/flush/release messages to MDS.
- Handles MDS cap messages: grant, revoke, import, export, trunc, flush ack, flushsnap ack.
- Coordinates dirty metadata flushing with inode writeback, fsync, snapshots, and MDS journal safety.
- Manages cap references for open files, buffered I/O, mmap, file locks, and cached pages.
- Encodes inode and dentry cap/lease releases into outgoing MDS requests.

## Core Concepts
- `issued`: caps the MDS currently wants the client to hold.
- `implemented`: caps the client still effectively holds, including caps being revoked but not yet returned due to active refs or dirty state.
- `wanted`: caps the client asks the MDS to keep/grant.
- `used`: caps with active local references, derived from ref counters and cache/writeback state.
- `dirty`: metadata caps that need to be flushed to the auth MDS.
- `flushing`: dirty metadata caps already sent but not acknowledged.
- `i_auth_cap`: the auth-MDS cap for the inode; only auth cap handles dirty metadata and max-size negotiation.
- `ceph_cap_snap`: snapshot-time metadata and dirty-page state that must be flushed in snap order.

## Cap Allocation and Reservation
- `ceph_caps_init()` / `ceph_caps_finalize()` initialize and drain the MDS client cap pool.
- `ceph_adjust_caps_max_min()` sets min/max cap cache sizing from mount options.
- `ceph_reserve_caps()` reserves cap objects before operations that may instantiate inodes/caps. It first consumes available caps, then allocates, then tries trimming session caps on allocation pressure.
- `ceph_unreserve_caps()` returns unused reservations and may trigger cap reclaim.
- `ceph_get_cap()` consumes a reservation or allocates/reuses a cap.
- `ceph_put_cap()` returns a cap to the pool or frees it once the pool exceeds the retained minimum.
- `ceph_reservation_status()` reports pool counters.

## Per-Inode Cap Storage
- Caps are stored in `ci->i_caps`, an rb-tree keyed by MDS id.
- `__get_cap_for_mds()` and `ceph_get_cap_for_mds()` look up caps.
- `__insert_cap_node()` inserts a new cap.
- Each cap is also linked into its session LRU list under `session->s_caps`.

## Cap Issuance and Wanted State
- `ceph_cap_string()` formats cap masks for diagnostics.
- `__cap_is_valid()` rejects stale caps based on session generation and TTL.
- `__ceph_caps_issued()` combines valid cap bits, includes snap caps, and excludes non-auth bits that the auth MDS is revoking.
- `__ceph_caps_issued_mask()` tests whether a mask is held, optionally touching cap LRU position.
- `__ceph_caps_file_wanted()` derives wanted caps from open modes and recent read/write activity.
- `__ceph_caps_used()` derives caps that must be retained because local refs/cache/writeback still exist.
- `__ceph_caps_wanted()` combines file-wanted and used caps, adding exclusives for dirty data or directory ops.
- `__ceph_caps_mds_wanted()` reports caps previously advertised to MDS.

## Adding and Removing Caps
- `ceph_add_cap()` creates or updates a cap from MDS grant/import data:
  - links it to inode and session;
  - updates snap realm;
  - updates auth cap selection;
  - records `issued`, `implemented`, seq/mseq, wanted, and generation;
  - queues delayed checks when issued caps exceed local wanted state.
- `__ceph_remove_cap()` removes a cap from inode/session structures, optionally queues release, updates auth cap, and drops snap realm when no real caps remain.
- `ceph_remove_cap()` wraps removal and warns if an auth cap with dirty state is removed unexpectedly.
- `__ceph_remove_caps()` removes all caps on inode teardown.

## Dirty Metadata and Cap Flush
- `__ceph_mark_dirty_caps()` marks metadata caps dirty, installs a preallocated cap-flush object, creates/holds head snap context if necessary, links the inode into the auth session dirty list, and returns VFS dirty flags.
- `__mark_caps_flushing()` moves dirty caps to flushing state, assigns a monotonically increasing flush tid, links into global and inode flush lists, and records oldest flush tid.
- `__prep_cap()` mutates cap state for an outgoing update/flush message and fills `cap_msg_args` with inode metadata, xattrs, time fields, size, max_size, fscrypt auth, dirty mask, wanted mask, and pending-capsnap flags.
- `encode_cap_msg()` marshals `CEPH_MSG_CLIENT_CAPS` version 12, including inline version, epoch barrier, oldest flush tid, btime/change_attr, advisory flags, dirstats placeholders, and fscrypt fields.
- `__send_cap()` allocates and sends the MDS caps message; on allocation failure it requeues delayed cap work.

## Snapshot Metadata Flushing
- `__ceph_flush_snaps()` walks `ci->i_cap_snaps` in order, waits until dirty pages and sync writes are complete, assigns flush tids, and sends `CEPH_CAP_OP_FLUSHSNAP`.
- `ceph_flush_snaps()` finds the auth session, kicks earlier flushing caps if needed, calls the internal flusher, and removes the inode from the snap flush queue.
- `ceph_try_drop_cap_snap()` removes capsnaps that have no associated snapshot flush work.
- `ceph_put_wrbuffer_cap_refs()` decrements dirty page refs for head or capsnap contexts, completes capsnaps when dirty pages reach zero, and triggers snap flushing or cap checking.

## Cap Checking State Machine
- `ceph_check_caps()` is the central reconciliation function:
  - computes file-wanted, used, issued, implemented, revoking, retain masks;
  - attempts nonblocking page-cache invalidation when cache/lazy caps are revoked and there is no dirty data;
  - decides whether to ack revocation, flush dirty metadata, request more max size, report size, update wanted caps, or release unneeded caps;
  - sends cap update/flush messages outside `i_ceph_lock`;
  - queues writeback for buffer-cap revocation blocked by dirty pages;
  - queues async invalidation when page-cache invalidation cannot complete inline.
- Delayed cap release uses:
  - `__cap_delay_requeue()`
  - `__cap_delay_requeue_front()`
  - `__cap_delay_cancel()`
  - `ceph_check_delayed_caps()`

## Getting and Releasing Cap References
- `try_get_cap_refs()` attempts to take references for needed/wanted caps:
  - handles file-lock error state;
  - resolves pending truncates;
  - validates max-size for writes;
  - waits for pending cap snaps before write refs;
  - avoids reordering buffered and synchronous writes by respecting revoking buffer caps;
  - handles readonly sessions, shutdown inodes, stale wanted state, and snap rwsem acquisition.
- `ceph_try_get_caps()` is a nonblocking read-cap helper.
- `__ceph_get_caps()` blocks until caps are available, handles signals, max-size requests, cap renewal, inline data fetch, and open-file generation checks.
- `ceph_get_caps()` is the file-based wrapper.
- `ceph_take_cap_refs()` increments per-inode cap ref counters and creates head snap context for writes.
- `ceph_put_cap_refs()` / `ceph_put_cap_refs_async()` drop refs synchronously or by queued work.
- `ceph_get_fmode()`, `ceph_put_fmode()`, and `__ceph_touch_fmode()` maintain open-mode counters and recent-use timestamps.

## fsync and write_inode
- `try_flush_caps()` sends dirty cap metadata immediately or marks the latest flushing tid for waiters.
- `caps_are_flushed()` tests whether flush list has advanced beyond a tid.
- `flush_mdlog_and_wait_inode_unsafe_requests()` asks relevant MDS sessions to flush their journals and waits for unsafe directory/inode operations to become safe.
- `ceph_fsync()` waits data writeback, flushes dirty non-file metadata caps, waits unsafe MDS requests, and checks writeback errors.
- `ceph_write_inode()` flushes or queues dirty caps depending on writeback mode and `for_sync`.

## MDS Message Handling
- `ceph_handle_caps()` decodes MDS cap messages, including optional versioned fields:
  - flock payload
  - import/export peer
  - inline data
  - OSD epoch barrier
  - pool namespace
  - btime/change_attr
  - advisory flags and dirstats
  - fscrypt auth/file-size fields
- It locates the inode, serializes on session mutex, and dispatches:
  - `CEPH_CAP_OP_GRANT` / `REVOKE` to `handle_cap_grant()`
  - `CEPH_CAP_OP_FLUSH_ACK` to `handle_cap_flush_ack()`
  - `CEPH_CAP_OP_FLUSHSNAP_ACK` to `handle_cap_flushsnap_ack()`
  - `CEPH_CAP_OP_TRUNC` to `handle_cap_trunc()`
  - `CEPH_CAP_OP_EXPORT` to `handle_cap_export()`
  - `CEPH_CAP_OP_IMPORT` to `handle_cap_import()` followed by grant handling
- If the inode/cap is missing, it may synthesize and flush a cap release so the MDS can make progress.

## Grant/Revoke/Import/Export Handling
- `handle_cap_grant()`:
  - applies inode metadata updates when shared caps permit;
  - updates xattrs, times, layout, dirstats, file size, max size, inline data, and fscrypt warnings;
  - invalidates page cache on cache-cap revoke when possible;
  - detects revoked buffer caps and queues writeback;
  - updates `issued` and `implemented`;
  - wakes cap waiters and queues truncation/invalidation/writeback as needed.
- `handle_cap_flush_ack()` removes acknowledged flush tids, clears flushing caps, releases inode refs, wakes inode/global waiters, and frees cap-flush objects.
- `handle_cap_flushsnap_ack()` removes acknowledged capsnaps and releases snap context/inode refs.
- `handle_cap_trunc()` applies MDS truncate state and queues vmtruncate when needed.
- `handle_cap_export()` migrates cap authority away from a session, creates target placeholders if needed, moves flushing list ownership, and removes old caps.
- `handle_cap_import()` installs imported auth caps, resolves peer exported caps, and returns the prior issued mask for grant handling.

## Release Encoding
- `ceph_drop_caps_for_unlink()` proactively drops link caps and queues dirty-cap flush work for soon-to-be-unlinked files.
- `ceph_encode_inode_release()` encodes cap release records into outgoing MDS requests, dropping only unused clean caps and respecting `unless` masks.
- `ceph_encode_dentry_release()` additionally drops dentry leases and encrypts dentry names when needed.
- `ceph_flush_dirty_caps()` and `ceph_flush_cap_releases()` iterate sessions to force dirty-cap or release flushing.

## Purge/Error Paths
- `ceph_purge_inode_cap()` removes a cap, and for auth caps:
  - invalidates page cache on shutdown with cached pages;
  - marks mapping error when dirty buffers remain;
  - drops dirty/flushing state;
  - marks file locks errored;
  - frees preallocated cap flushes;
  - removes capsnaps.
- `invalidate_aliases()` prunes/drops dentries when link count reaches zero.

## External Dependencies
- Ceph MDS session/client logic, snap realms, request queues, and reconnect behavior.
- Ceph OSD epoch barrier update.
- Linux VFS inode writeback, wait queues, file locks, dentries, and inode versioning.
- FS-Cache invalidation helpers.
- Ceph fscrypt auth fields and encrypted dentry encoding.

## Risk Notes
- This file is concurrency-heavy: correctness depends on lock ordering among `i_ceph_lock`, session mutexes, `snap_rwsem`, `cap_dirty_lock`, `cap_delay_lock`, and session cap locks.
- `issued` vs `implemented` distinction is essential for safe revocation under active refs.
- Dirty/flushing cap lists carry inode references; missing put paths can leak inodes, while premature puts can lose dirty metadata.
- Cap migration import/export sequence handling must preserve auth-cap and flushing ownership.
- fscrypt file sizes differ from rounded wire sizes, so grant/trunc/cap message encoding must use the right size field.
