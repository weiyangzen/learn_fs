# File Research: sources/os/linux/linux-stable/fs/afs/internal.h

## Summary
Central private header for the Linux AFS client. It defines core structures, flags, state machines, inline helpers, and cross-file function declarations for cells, volumes, servers, vnodes, calls, operations, directory iteration, probing, locking, security, rxrpc, validation, and YFS support.

## Main Contents
- Mount context: `struct afs_fs_context`.
- RxRPC call model: `struct afs_call`, `struct afs_call_type`, call-state enum.
- Address and server discovery: address preferences, `afs_addr_list`, VL server structures, fileserver endpoint state.
- Cell/volume/server lifecycle structures.
- Vnode/inode state: `struct afs_vnode`, callback state, directory cache, locks, writeback keys.
- Operation wrapper: `struct afs_operation`, `struct afs_vnode_param`, `struct afs_operation_ops`.
- Permit cache, symlink cache, error accumulator, VL cursor, server rotation state.
- Declarations for all internal AFS source modules.
- Inline helpers for network namespace lookup, fscache auxiliary data, callbacks, directory invalidation, call extraction, and debug assertions.

## Key Interfaces
Declares APIs for:
- Directory search/edit/silly rename/dynroot/mountpoint handling.
- File operations, netfs request ops, writeback, and mmap invalidation.
- Fileserver RPC stubs, operations, probes, rotation, and server management.
- Inode lifecycle and validation.
- Security key/permit lookup.
- VLDB/VL server probing and volume management.
- YFS enhanced RPC variants and opaque ACL support.

## Important Details
`struct afs_vnode` embeds `struct netfs_inode` and stores AFS FID/status, callback counters, validation locks, directory and symlink caches, writeback keys, file lock queues, and mmap callback tracking.

`struct afs_operation` is the shared execution envelope for fileserver operations. It stores vnode params, dentries, mtime/ctime, operation-specific unions, cumulative errors, current server/address selection, and flags controlling retry, locking, async mode, and directory conflict handling.

`afs_make_op_call()` binds a prepared `afs_call` to the selected endpoint in `op->estate->addresses` and dispatches it through rxrpc. Extraction helpers set the call iterator for temporary fields, fixed buffers, or discard.

## Risks
This header is a dense coupling point: structure layout, flag semantics, and inline lifetime helpers are depended on across the entire AFS client. Many fields are protected by different locks or RCU domains, so consumers must follow the documented owning subsystem conventions.
