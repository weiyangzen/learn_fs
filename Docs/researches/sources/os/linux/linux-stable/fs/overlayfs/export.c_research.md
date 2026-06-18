# File Research: sources/os/linux/linux-stable/fs/overlayfs/export.c

## Scope

This file implements overlayfs exportfs/NFS file-handle support: deciding upper vs lower handle encoding, forcing copy-up of connectable ancestors, encoding overlay file handles, decoding upper/lower handles back to overlay dentries, consulting index/origin metadata, reconnecting directory paths, and exposing export operation tables.

## Public And Internal APIs Covered

- Export ops: `ovl_encode_fh()`, `ovl_fh_to_dentry()`, `ovl_fh_to_parent()`, `ovl_get_name()`, `ovl_get_parent()`.
- Operation tables: `ovl_export_operations` and `ovl_export_fid_operations`.
- Encoding helpers: `ovl_check_encode_origin()`, `ovl_connect_layer()`, `ovl_connectable_layer()`, `ovl_dentry_to_fid()`.
- Decode/reconnect helpers: `ovl_upper_fh_to_d()`, `ovl_lower_fh_to_d()`, `ovl_fid_to_fh()`, `ovl_get_dentry()`, `ovl_obtain_alias()`, `ovl_lookup_real()`, `ovl_lookup_real_ancestor()`, `ovl_lookup_real_inode()`, `ovl_lookup_real_one()`.

## Control Flow And Behavior

- Encoding usually uses lower file handles for non-upper or indexed-origin objects to preserve stable identity across copy-up, and upper file handles for pure upper, non-indexed upper, and root.
- For decodable NFS export of lower directories, `ovl_connect_layer()` may copy up a connectable ancestor before encoding so future decode can reconnect from the lower real dentry to an overlay dentry.
- `ovl_dentry_to_fid()` encodes either an upper or lower real inode with `ovl_encode_real_fh()` and returns the byte length needed by exportfs.
- Connectable parent file handles are not supported; `fh_to_parent` returns `-EACCES` and warns to use `no_subtree_check`.
- Decoding upper handles requires an upper mount and maps the decoded upper dentry into an overlay dentry.
- Decoding lower handles first validates origin file handles and layer acceptability, checks inode cache aliases, consults index entries, verifies origin/index consistency, then obtains a connected directory dentry or disconnected non-directory alias.
- Directory reconnect walks from a known connected ancestor toward the target real dentry, looking up overlay children by real names and restarting if overlay rename races break parentage.
- Old unaligned file-handle format `OVL_FILEID_V0` is copied into an aligned buffer before validation.

## State And Data Structures

- Uses `struct ovl_fh` encoded inside exportfs `fid` buffers, including flags such as `OVL_FH_FLAG_PATH_UPPER`.
- Uses overlay layers, lower stacks, index dentries, origin handles, dcache aliases, and inode hash lookups.
- `OVL_E_CONNECTED` dentry flag caches positive connected-layer results.

## Dependencies

- Depends on exportfs encoding/decoding, overlayfs origin/index helpers, copy-up, lookup, dentry allocation, inode lookup, layer metadata, and real path decoding.
- Uses dentry name snapshots to avoid use-after-free when racing with underlying layer rename.

## Risks And Invariants

- Non-connectable lower directory handles must be made connectable at encode time or decode can fail later.
- Directory decode must reject disconnected, unhashed, moved-out, or stale underlying dentries.
- Inode/dentry cache aliases are verified against real upper/lower dentries to avoid returning mismatched overlay objects.
- `fh_to_parent`, `get_name`, and `get_parent` are intentionally unsupported for subtree-check style export.
