# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_exchmaps.h

## Purpose

`xfs_exchmaps.h` declares the in-core data structures and API for XFS mapping exchange operations. It separates caller-facing requests from deferred-operation intents and exposes estimation, scheduling, and worker hooks.

## Main Types

`struct xfs_exchmaps_intent` stores deferred operation state:

- List linkage for deferred work.
- Two participating inodes.
- Current start offsets and remaining block count.
- Optional final file sizes.
- Operation flags, including internal cleanup flags.

`struct xfs_exchmaps_req` is the caller-provided request:

- Two inodes.
- Start offsets and block count.
- Public operation flags.
- Estimator-filled accounting fields: blocks moved out of each inode, realtime blocks, reserved blocks, and number of exchanges.

## Flags and Fork Selection

`__XFS_EXCHMAPS_INO2_SHORTFORM` is an internal high-bit flag asking post-op cleanup to try converting inode2 back to shortform/local format.

`XFS_EXCHMAPS_INTERNAL_FLAGS` currently contains only the shortform cleanup bit.

`XFS_EXCHMAPS_PARAMS` defines the public parameter subset accepted by estimation: attr-fork exchange, final size exchange, and the optimization stating inode1's relevant mappings are written.

`xfs_exchmaps_whichfork` and `xfs_exchmaps_reqfork` translate the attr-fork flag into `XFS_ATTR_FORK` or default to `XFS_DATA_FORK`.

## API Surface

Declared functions include:

- `xfs_exchmaps_estimate_overhead` and `xfs_exchmaps_estimate` for preflight reservation and extent-count estimates.
- Slab cache lifecycle: `xfs_exchmaps_intent_init_cache` and `xfs_exchmaps_intent_destroy_cache`.
- `xfs_exchmaps_init_intent` to allocate an in-core intent from a request.
- `xfs_exchmaps_ensure_reflink` and `xfs_exchmaps_upgrade_extent_counts` for pre-operation inode flag preparation.
- `xfs_exchmaps_finish_one` for deferred-operation execution.
- `xfs_exchmaps_check_forks` to reject unsupported fork states.
- `xfs_exchange_mappings` to schedule a deferred mapping exchange from a transaction.

## Dependencies and Role

This header is consumed by the exchange-maps implementation, exchange-maps log item/recovery code, and callers preparing range exchange operations. It deliberately exposes request/intent structure fields because the deferred operation and log item layers need to serialize, relog, recover, and continue the operation.
