<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_aio_ratelimit.c -->
# sources/user-network-fs/samba/source3/modules/vfs_aio_ratelimit.c

## Purpose
This stackable VFS module rate-limits asynchronous read and write operations with token buckets. It can enforce per-share IOPS and bandwidth ceilings, inject tevent delays before dispatching async I/O, and persist token state across reconnects/restarts in a local TDB.

## Important APIs, Types, And Functions
Important types are `struct ratelimit_tdb_record`, `struct ratelimiter`, `struct vfs_aio_ratelimit_config`, and `struct vfs_aio_ratelimit_state`. Key helpers include TDB version/init/load/save functions, `ratelimiter_init`, `ratelimiter_refill`, `ratelimiter_pre_io`, `ratelimiter_post_io`, config parsing helpers, connect/disconnect, and async pread/pwrite send/waited/done/recv functions.

## Control Flow
Connect opens `aio_ratelimit.tdb` if possible, then creates per-handle read/write ratelimiters from `aio_ratelimit:*` parameters. Before each async pread or pwrite, `ratelimiter_pre_io` refills tokens based on monotonic time, consumes one IOP token and requested byte tokens, computes the maximum deficit-derived delay, updates counters, and periodically saves state. If no delay is required, the request is passed immediately to the next VFS async operation. Otherwise a `tevent_wakeup_send` delay is scheduled, and the next VFS operation starts after the wakeup. Completion calls `ratelimiter_post_io` to credit unused byte tokens when short I/O occurs.

## State And Persistence
Per-connection ratelimiters hold token counters, capacities, totals, timestamps, burst multiplier, and share number. Process-global `ratelimit_tdb` is refcounted and stores records under `share/<servicename>/<read|write>` with schema version `RATELIMIT_TDB_VERSION`. TDB failure is non-fatal; limiting continues without persistence.

## Dependencies And Integration Points
The module depends on Samba tevent, VFS async pread/pwrite hooks, tdb, state paths, loadparm parsing including size strings, monotonic time helpers, and root privilege helpers for TDB open. It registers as `aio_ratelimit` and is meant to stack above an async I/O provider.

## Risks
Token fields are floats, so long-running precision and serialization stability matter. The TDB key is per share/service and operation, not per client, so limits are shared across connections to a share. Maximum injected delay is capped at 100 seconds. Refcount decrement assumes a successful init path; careful connect/disconnect pairing is needed. Delays are applied before the lower async I/O starts, so they rate-limit response flow but do not cancel queued requests.

## Test Signals
Tests should cover disabled limits, IOPS-only, bandwidth-only, combined limits, burst multiplier behavior, short I/O token refund, TDB version mismatch, persistence across reconnect, invalid bandwidth config strings, delay cap, read and write independent buckets, and stacking with an async backend.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_aio_ratelimit.c -->
