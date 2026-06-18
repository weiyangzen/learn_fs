# File Research: sources/local-fs/xfsprogs/libxfs/xfs_log_recover.h

## Role

This header defines internal interfaces and structures for XFS log recovery. It binds recovered log item types to per-type recovery operations and declares helpers for recovery item ordering, readahead, inode lookup, intent handling, and buffer cancellation tables.

## Main Structures

`enum xlog_recover_reorder` classifies recovered items into replay queues:

- normal buffer list
- normal item list
- inode buffer list
- cancel list

`struct xlog_recover_item_ops` supplies per-log-item recovery behavior:

- item type code
- optional reorder callback
- optional pass2 readahead callback
- optional pass1 commit callback
- pass2 commit callback

The pass2 comments define intent/done recovery semantics: intent items reconstruct incore intent log items in the AIL with one reference; done items find and release corresponding intents.

`struct xlog_recover_item` stores recovered regions and the item ops. `struct xlog_recover` stores partial transaction reconstruction state.

## Declared Recovery Items

The header declares ops for icreate, buffer, inode, dquot, quotaoff, bmap, extent free, rmap, refcount, attr, mapping exchange, and realtime variants.

## Helpers And Constants

- `XLOG_RHASH_*` constants hash transaction ids.
- `XLOG_MAX_REGIONS_IN_ITEM` derives a maximum from block size and buffer log chunking.
- `ITEM_TYPE` extracts the item type from the first region.
- Recovery pass constants identify CRC, pass1, and pass2 stages.
- `xlog_recover_resv` transforms normal transaction reservations into single-step intent recovery reservations by forcing `tr_logcount = 1`.

## Dependencies

Recovery uses `struct xlog`, transactions, inode lookup, defer operation types, log items, LSNs, buffer ops, and AIL intent management.

## Research Notes

The separation of pass1, pass2, reordering, and intent recovery is the main contract. The reservation helper prevents livelock when recovered intents pin the log tail.
