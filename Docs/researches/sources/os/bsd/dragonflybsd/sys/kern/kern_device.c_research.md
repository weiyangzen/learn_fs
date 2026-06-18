# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_device.c

## Purpose

Implements the DragonFlyBSD device-operation dispatch layer. It wraps `struct dev_ops` calls, supplies default/dead operations, handles Giant/MPLock compatibility for non-MPSAFE drivers, and provides helpers for operation interception and compilation.

## Key Responsibilities

- Defines `syslink_desc` descriptors for each device operation offset.
- Provides `default_dev_ops` and `dead_dev_ops`.
- Wraps device open/close/read/write/ioctl/mmap/strategy/dump/psize/kqfilter/clone/revoke calls.
- Applies MPLock around non-`D_MPSAFE` device operations.
- Handles KVABIO synchronization for device strategies when drivers lack `D_KVABIO`.
- Tracks per-device read/write I/O via `bio_track`.
- Fills missing `dev_ops` function pointers with default handlers.
- Supports temporary dev_ops interception/restoration.
- Exposes simple device metadata helpers.

## Main Entry Points

- `dev_dopen()`, `dev_dclose()`, `dev_dread()`, `dev_dwrite()`, `dev_dioctl()`.
- `dev_dmmap()`, `dev_dmmap_single()`.
- `dev_dclone()`, `dev_drevoke()`.
- `dev_dstrategy()` and `dev_dstrategy_chain()` submit block I/O strategies.
- `dev_ddump()` and `dev_dpsize()` support dump and size queries.
- `dev_dkqfilter()` forwards kqueue filter registration.
- `dev_drefs()`, `dev_dname()`, `dev_dflags()`, `dev_dmaj()` expose device metadata.
- `dev_doperate()` dispatches an operation by descriptor offset.
- `dev_doperate_ops()` dispatches through a foreign ops structure, used by console interception.
- `compile_dev_ops()` fills NULL operation slots.
- `dev_ops_remove_all()` and `dev_ops_remove_minor()` destroy devfs devices associated with ops.
- `dev_ops_intercept()` / `dev_ops_restore()` swap per-device ops for interception.

## Important Implementation Details

- `dev_needmplock()` checks `D_MPSAFE`; wrappers acquire/release `get_mplock()` around non-MPSAFE driver calls.
- `dev_nokvabio()` checks `D_KVABIO`; strategy wrappers call `bkvasync_all()` for KVABIO buffers if the driver cannot handle them.
- `dev_dstrategy()` asserts no existing `bio_track`, selects read/write tracking, enters disk scheduler accounting via `dsched_buf_enter()`, and dispatches.
- `dev_dstrategy_chain()` assumes `bio_track` was already set by an upstream chained strategy path.
- `compile_dev_ops()` iterates from `dev_ops_first_field` through `dev_ops_last_field`, assigning either `d_default` or the `default_dev_ops` slot.
- Default unsupported ops generally return `ENODEV`; default strategy marks the buffer `B_ERROR`, sets `EOPNOTSUPP`, and calls `biodone()`.

## Data and Registration

- `DEVOP_DESC_INIT()` creates operation descriptors such as `dev_open_desc`, `dev_strategy_desc`, and `dev_ioctl_desc`.
- `default_dev_ops` supplies fallback implementations.
- `dev_ops_rbhead` is declared with RB-tree generation for major-number tracking, though this file’s visible add/remove paths are delegated to devfs helpers.
- `dead_dev_ops` exists for destroyed devices and is referenced by other device code.

## Filesystem/Storage Relevance

This file is the call path between VFS/device vnodes and block/character drivers. Storage I/O reaches device drivers through `dev_dstrategy()` and related wrappers, so this layer mediates locking, buffer mapping constraints, disk scheduler entry, and error fallback behavior.

## Research Notes

- Strategy path comments distinguish normal and chained BIO submission; chained submission intentionally does not push a new tracking structure.
- Operation interception copies major/data/flags from old ops to interceptor ops, sets `SI_INTERCEPTED`, then restores and clears those fields later.
- Default `noclone()` returns success, allowing clone unless a driver overrides it.
