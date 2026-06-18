# File Research: sources/os/linux/linux-stable/fs/ubifs/misc.h

## Summary
Defines inline UBIFS helpers used across the filesystem for TNC state checks, compressor metadata, write-buffer synchronization, lprops locking, index-node layout, log wrapping, and xattr limits.

## Main Contents
- Znode flag helpers: `ubifs_zn_dirty()`, `ubifs_zn_obsolete()`, `ubifs_zn_cow()`.
- Background-thread wakeup: `ubifs_wake_up_bgt()`.
- TNC helpers: `ubifs_tnc_find_child()`, `ubifs_tnc_lookup()`.
- Inode/container helper: `ubifs_inode()`.
- Compression helpers: `ubifs_compr_present()`, `ubifs_compr_name()`.
- Write-buffer helper: `ubifs_wbuf_sync()`.
- Device encoding: `ubifs_encode_dev()`.
- Lprops helpers: `ubifs_add_dirt()`, `ubifs_return_leb()`, `ubifs_get_lprops()`, `ubifs_release_lprops()`.
- Index helpers: `ubifs_idx_node_sz()`, `ubifs_idx_branch()`, `ubifs_idx_key()`.
- Log/xattr helpers: `ubifs_next_log_lnum()`, `ubifs_xattr_max_cnt()`.

## Important Behavior
Most functions are thin wrappers that encode UBIFS invariants at call sites. `ubifs_wbuf_sync()` acquires the journal-head nested I/O mutex before calling the nolock sync path. `ubifs_get_lprops()` and `ubifs_release_lprops()` centralize `lp_mutex` use and assert sane empty-LEB accounting before unlock.

Index-node helpers account for variable key and hash lengths in authenticated configurations. `ubifs_next_log_lnum()` wraps from `log_last` back to `UBIFS_LOG_LNUM`.

## Dependencies
Includes `ubifs.h` types and global compressor table declarations. The helpers call TNC, lprops, write-buffer, Linux device encoding, and mutex APIs.

## Risks
Because this header is included broadly, subtle layout helpers such as `ubifs_idx_branch()` and `ubifs_idx_node_sz()` must stay synchronized with on-flash index format changes. Locking wrappers assume callers respect the lprops lock lifetime.
