# File Research: sources/os/linux/linux-stable/fs/overlayfs/namei.c

## Purpose

`namei.c` implements overlayfs lookup, origin/index file-handle verification, redirect following, metacopy lower-data discovery, and helper traversal over overlay path layers. It is the main name-resolution path that turns an overlay dentry name into an overlay inode backed by an optional upper dentry and one or more lower dentries.

## Main Responsibilities

- Validate and decode overlay file-handle xattrs used for origin/index identity.
- Lookup names in upper and lower layers while respecting whiteouts, opaque dirs, redirects, xwhiteouts, metacopy, casefold state, and trap inodes.
- Resolve data-only lower layers through absolute lowerdata redirects, with lazy lowerdata lookup on first access.
- Verify origin/index consistency for `index=on` and `nfs_export=on`.
- Instantiate overlay inodes with `ovl_get_inode()` and initialize dentry revalidation flags.
- Provide layer iteration through `ovl_path_next()` and lower existence probing through `ovl_lower_positive()`.

## Key Types And State

- `struct ovl_lookup_data`: per-lookup mutable state, including current layer, name, type flags, opaque/stop state, redirect buffers, metacopy state, and whether the active redirect is absolute.
- `struct ovl_lookup_ctx`: lifetime container for lookup outputs: upper dentry, lower stack, origin path, index dentry, overlay entry, inode, and lower count.
- `struct ovl_fh` / `struct ovl_fb`: overlay file-handle formats defined in `overlayfs.h` and validated here.
- Lower stack entries use `struct ovl_path` from `ovl_entry.h`.

## Important Functions

- `ovl_check_fb_len()` validates origin/index file-handle buffers, treating unknown versions, unknown flags, and endian mismatch as "origin unknown" (`-ENODATA`) rather than fatal corruption.
- `ovl_uuid_match()` checks whether a stored file-handle UUID matches a candidate layer superblock, or requires null UUID when origin UUID storage is disabled.
- `ovl_decode_real_fh()` decodes a real lower/upper dentry from a file handle using exportfs and rejects weird dentries.
- `ovl_check_origin_fh()` scans lower layers for a decodable origin and fills a one-entry `ovl_path`.
- `ovl_verify_set_fh()` and `ovl_verify_origin_xattr()` compare xattr file handles against encoded real dentries, optionally setting missing xattrs.
- `ovl_index_upper()`, `ovl_verify_index()`, `ovl_get_index_name*()`, `ovl_get_index_fh()`, and `ovl_lookup_index()` implement index directory validation and lookup.
- `ovl_lookup_layer()` and `ovl_lookup_single()` perform path lookup within one real layer, including redirect, whiteout, opacity, metacopy, and trap checks.
- `ovl_lookup_layers()` coordinates complete upper/lower lookup and builds the overlay inode inputs.
- `ovl_lookup()` is the exported inode operation lookup entry.
- `ovl_verify_lowerdata()` performs lazy lowerdata lookup and fs-verity digest validation.
- `ovl_lower_positive()` checks whether a dentry has a positive lower entry despite upper state.

## Lookup Flow

`ovl_lookup()` rejects names longer than `ofs->namelen`, enters overlay credentials, and calls `ovl_lookup_layers()`.

`ovl_lookup_layers()` first searches the upper parent if present. A found upper dentry may provide an origin xattr and may carry redirect or metacopy state. If the upper lookup finds an absolute redirect, lookup restarts against the root lower stack.

The lower-stack pass walks each lower layer from top to bottom. Each layer lookup rejects unsupported objects, validates casefold consistency, handles whiteouts, treats `overlay.opaque=y` as a stop marker, treats `overlay.opaque=x` as an xwhiteout directory marker, and follows valid redirects when allowed. Metacopy entries are kept only when they are meaningful for the topmost metadata object; lower data is required before lookup succeeds.

When data-only lower layers are configured, an absolute lowerdata redirect can defer final data lookup. The inode stores the redirect and later `ovl_verify_lowerdata()` resolves it with `ovl_lookup_data_layers()`.

If an origin is known and indexing is enabled, `ovl_lookup_index()` validates the index entry against the current upper/origin pair. The final inode parameters include upper dentry, lower stack, index flag, redirect, and optional lazy lowerdata redirect. Dentry flags are initialized after inode creation.

## Index And Origin Invariants

Index entry names are hex-encoded lower origin file handles. Directory index entries carry an upper file-handle xattr pointing at the associated upper dir, while non-directory index entries are hardlinks to upper inodes. `ovl_verify_index()` rejects malformed names, stale origins, incompatible types, bad whiteouts, and orphan entries; NFS export tightens verification.

Origin verification is deliberately nuanced: stale lower handles can be treated as unknown in non-fatal cases, but explicit mismatches during index or NFS export paths become stale/error outcomes to avoid aliasing corruption.

## Dependencies And Integration

This file depends heavily on:

- `util.c` for xattr helpers, whiteout checks, redirect/metacopy helpers, lowerdata setters, copy-up state, and fs-verity validation.
- `super.c` mount-time feature choices such as `index`, `metacopy`, `redirect_mode`, `nfs_export`, `uuid`, `xino`, and data-only layer layout.
- `inode.c` for `ovl_get_inode()`, origin trap checks, inode initialization, and nlink helpers.
- `readdir.c` indirectly through xwhiteout and whiteout semantics.
- VFS/exportfs/namei APIs such as `lookup_one_unlocked()`, `vfs_path_lookup()`, `exportfs_decode_fh()`, and dentry revalidation flags.

## Risk Notes

- Redirect following is security-sensitive because it can expose lower paths without normal path permission checks; `ovl_check_follow_redirect()` enforces mount-feature gating.
- Index/origin xattrs are consistency-critical for NFS export and hardlink identity.
- Lazy lowerdata lookup uses memory ordering through `ovl_dentry_set_lowerdata()` in `util.c`; consumers must respect those helpers.
- Casefold consistency is enforced during lookup, but offline lower modifications can still invalidate assumptions.
- Stale lower file handles are sometimes tolerated to preserve compatibility, so feature combinations that require strong identity rely on mount-time checks and index verification.
