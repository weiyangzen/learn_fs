# File Research: sources/os/linux/linux/fs/overlayfs/export.c

## Role

Implements OverlayFS exportfs/NFS file handle encoding and decoding.

## Main Responsibilities

- Decides whether to encode upper or lower/origin file handles.
- Copies up connectable ancestors before encoding lower directory handles when needed for later decode.
- Encodes non-connectable file handles only; parent/connectable file handles are rejected.
- Obtains overlay dentries from real upper/lower dentries, origin file handles, and index entries.
- Resolves decoded lower handles through inode cache, index dir, origin verification, and connected path lookup.
- Supports legacy `OVL_FILEID_V0` by realigning unaligned on-wire inner file handles.
- Exposes full `ovl_export_operations` for NFS export and encode-only `ovl_export_fid_operations` when handles need not be decodable.

## Important Control Flow

`ovl_check_encode_origin()` selects the file handle identity. Pure upper and non-indexed upper objects generally encode upper handles. Indexed upper and non-upper objects encode lower handles. For decodable directory handles, `ovl_connect_layer()` may copy up an ancestor to ensure later reconstruction can find a connected overlay path.

Decode flows split by `OVL_FH_FLAG_PATH_UPPER`. Upper handles decode through the upper mount and `ovl_get_dentry()`. Lower handles decode by checking origin file handles, consulting cached overlay inodes, looking up index entries, verifying origin consistency, and then obtaining connected or disconnected overlay dentries as appropriate.

## Lookup Strategy

`ovl_lookup_real()` walks from a known connected overlay ancestor toward the target real dentry. It uses name snapshots to avoid racing real dentry renames and restarts from ancestors on `-ECHILD` races.

## Limitations

`fh_to_parent`, `get_name`, and `get_parent` are effectively unsupported for connectable file handles; the code warns to use `no_subtree_check`.

## Dependencies

Relies on origin/index xattrs, lower layer descriptors, exportfs handle encoding/decoding, dcache alias lookup, and OverlayFS copy-up/index helpers.

## Research Notes

This file encodes the complex relationship between union dentries and persistent NFS handles. Index and redirect correctness are essential for stable decode.
