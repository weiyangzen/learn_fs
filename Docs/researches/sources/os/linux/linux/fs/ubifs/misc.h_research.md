# File Research: sources/os/linux/linux/fs/ubifs/misc.h

## Role

Defines small inline helpers used broadly across UBIFS for znode state, background-thread wakeup, inode conversion, compressor metadata, write-buffer sync, device encoding, lprops locking, LPT/lprops updates, index-node layout, TNC lookup, log wraparound, and xattr limits.

## Key APIs

- Znode flags: `ubifs_zn_dirty()`, `ubifs_zn_obsolete()`, `ubifs_zn_cow()`
- Runtime helpers: `ubifs_wake_up_bgt()`, `ubifs_inode()`
- Compression helpers: `ubifs_compr_present()`, `ubifs_compr_name()`
- I/O/lprops helpers: `ubifs_wbuf_sync()`, `ubifs_add_dirt()`, `ubifs_return_leb()`
- Index helpers: `ubifs_idx_node_sz()`, `ubifs_idx_branch()`, `ubifs_idx_key()`
- TNC/log helpers: `ubifs_tnc_lookup()`, `ubifs_next_log_lnum()`
- Locking: `ubifs_get_lprops()`, `ubifs_release_lprops()`
- Xattr limit: `ubifs_xattr_max_cnt()`

## Important Behavior

The znode helpers are thin wrappers over znode flag bits. `ubifs_wake_up_bgt()` wakes the background thread only when present and not already requested.

`ubifs_wbuf_sync()` locks the write-buffer I/O mutex with the journal-head subclass, calls the no-lock sync helper, and unlocks.

Index helpers encode UBIFS variable key/hash length into index-node and branch pointer arithmetic. `ubifs_tnc_lookup()` is a convenience wrapper over `ubifs_tnc_locate()`.

Lprops helpers centralize lock acquisition/release and include sanity assertions on release. `ubifs_add_dirt()` and `ubifs_return_leb()` route common lprops mutations through the lprops update APIs.

`ubifs_next_log_lnum()` wraps log LEB numbers from `log_last` back to `UBIFS_LOG_LNUM`.

## Dependencies

Depends on UBIFS core types, Linux inode/container helpers, bit operations, mutexes, device encoding helpers, compressor registry, write-buffer code, TNC lookup, and lprops mutation APIs.

## Research Notes

This header is a low-level convenience layer. Several helpers encode important contracts: callers of `ubifs_get_lprops()` must release through `ubifs_release_lprops()`, and index branch arithmetic must stay aligned with the on-flash index format.
