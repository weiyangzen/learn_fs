# File Research: sources/os/linux/linux/fs/afs/internal.h

## Purpose
Central internal header for the Linux AFS client. It defines shared structures, state enums, flags, inline helpers, operation contracts, and cross-file prototypes.

## Main Responsibilities
- Defines mount context, per-network namespace, cell, VL server, fileserver, volume, vnode, call, operation, callback, permit, and address-list data models.
- Declares all major AFS subsystem entry points used across the directory, cell, server, volume, RPC, validation, writeback, lock, proc, and mountpoint code.
- Provides inline helpers for net namespace lookup, vnode/inode conversion, call state transitions, reply extraction setup, callback promise state, dentry data-version updates, and operation error accumulation.
- Defines debugging and assertion macros used throughout the AFS client.

## Key Structures
- `struct afs_net`: per-net namespace state, including cells, server probe queues, proc entries, socket state, sysnames, address preferences, and counters.
- `struct afs_cell`: cell identity, VL server list, root volume, DNS state, alias tracking, proc links, and dynamic-root inode allocation.
- `struct afs_server` / `struct afs_endpoint_state`: fileserver identity, endpoint list, probe state, service/capability flags, and RTT/preferred-address data.
- `struct afs_volume`: live volume state, server list, fscache volume, callback counters, volume type/name, and open mmap list.
- `struct afs_vnode`: inode-private state including fid, status, callback promise, locks, directory/symlink data, writeback keys, permit cache, and netfs inode.
- `struct afs_operation`: high-level fileserver operation wrapper for vnode params, RPC selection, server/address rotation, cumulative errors, and operation-specific unions.
- `struct afs_call`: RxRPC call state, request/reply buffers, iterator state, call type, server/probe refs, error/abort state, and unmarshalling scratch fields.

## Key Contracts
- `struct afs_operation_ops` supplies `issue_afs_rpc`, `issue_yfs_rpc`, `success`, `aborted`, `failed`, `edit_dir`, and `put` hooks.
- `afs_make_op_call()` binds an operation-selected server endpoint to a call and invokes `afs_make_call()`.
- `afs_set_call_complete()` atomically transitions call state to complete, records local/remote errors, traces, and drops deferred refs when needed.
- `afs_op_set_vnode()` marks a vnode parameter as needing the operation I/O lock by default.
- `afs_invalidate_dir()` clears directory-valid state and bumps invalidation stats only on first transition.

## Important Details
- Vnode lock states enumerate the whole server lock lifecycle from no lock through waiting, setting, granted, extending, unlocking, and deleted.
- AFS operation flags track stop/retry, volume errors, current-server-only, uninterruptible operation, held I/O locks, directory conflict, async mode, and opcode downgrade.
- Callback promise expiration uses `AFS_NO_CB_PROMISE == TIME64_MIN`.
- The header includes prototypes for both AFS3 and YFS RPC clients, reflecting the common operation layer.
- Assertion macros are enabled in the visible `#if 1` block, so failed `ASSERT*` checks call `BUG()`.
