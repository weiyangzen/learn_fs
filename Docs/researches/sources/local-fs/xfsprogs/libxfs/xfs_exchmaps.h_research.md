# File Research: sources/local-fs/xfsprogs/libxfs/xfs_exchmaps.h

## Purpose
Declares the public libxfs interface and data structures for XFS mapping exchange operations.

## Main Contents
- `struct xfs_exchmaps_intent` stores deferred in-core exchange state: inode pair, offsets, block count, optional final sizes, and operation flags.
- `struct xfs_exchmaps_req` is the caller-facing request plus estimator outputs such as moved block counts, reservation blocks, and number of exchange steps.
- `xfs_exchmaps_whichfork()` and `xfs_exchmaps_reqfork()` select data vs attr fork from flags.
- Defines internal flag `__XFS_EXCHMAPS_INO2_SHORTFORM` and accepted request parameter mask `XFS_EXCHMAPS_PARAMS`.
- Declares estimator, intent cache, intent creation, reflink preparation, extent-count upgrade, deferred step completion, fork validation, and scheduling functions.

## Integration
The header bridges higher-level exchange-range callers, deferred operation code, and the implementation in `xfs_exchmaps.c`. The request structure is intentionally split between caller-initialized inputs and fields filled by `xfs_exchmaps_estimate()`.

## Risks and Notes
`xfs_exchmaps_intent` is both deferred-work state and recovery-progress state, so flag semantics must remain compatible with logged exchange-map intent/done items. Internal flags are kept outside the logged flag namespace with a build-time assertion in the implementation.
