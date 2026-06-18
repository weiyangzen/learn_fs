# File Research: sources/os/linux/linux/fs/overlayfs/namei.c

## Purpose

`namei.c` implements overlayfs name lookup and identity verification. It resolves overlay dentries to upper and lower real dentries, follows overlay redirects when allowed, handles whiteouts/opaque directories/metacopy, verifies origin and index file handles, and creates overlay inodes from the resolved backing stack.

## Main Responsibilities

- Validate overlay file-handle buffers stored in `overlay.origin`, `overlay.upper`, and index names.
- Decode origin/index file handles back to real lower or upper dentries.
- Lookup a child in the upper layer and in the ordered lower layer stack.
- Follow relative and absolute overlay redirects, including redirects into data-only lower layers.
- Interpret whiteouts, opaque directories, xwhiteout markers, metacopy files, and overlapping-layer traps.
- Verify lower origin consistency for `index=on`, `nfs_export=on`, and `verify_lower` paths.
- Lookup and verify index-directory entries for copied-up objects and export support.
- Build `struct ovl_entry` lower stacks and pass `struct ovl_inode_params` to `ovl_get_inode()`.
- Lazily resolve lowerdata for metacopy files with absolute data-layer redirects.

## Key Types And State

- `struct ovl_lookup_data`: per-lookup mutable state, including the current layer, name, directory/metacopy/opaque state, redirect buffers, and whether the current redirect is absolute.
- `struct ovl_lookup_ctx`: owns lookup outputs such as upper dentry, lower stack, origin path, index dentry, allocated overlay entry, inode, and stack count.
- `struct ovl_fh` / `struct ovl_fb`: overlay file-handle wire format from `overlayfs.h`.
- `struct ovl_path`: pairs a resolved real dentry with its overlay layer.
- `d->stop`, `d->opaque`, `d->xwhiteouts`, and `d->metacopy`: lookup controls that determine whether lower-layer traversal continues.

## Important Functions

- `ovl_check_fb_len()` validates overlay file-handle body length, magic, version, flags, and endian compatibility.
- `ovl_uuid_match()` checks stored file-handle UUIDs against real layer superblock UUIDs, or requires null UUID when origin UUID storage is disabled.
- `ovl_decode_real_fh()` uses exportfs to decode a stored file handle and rejects unsupported or weird dentries.
- `ovl_lookup_positive_unlocked()` wraps `lookup_one_unlocked()` and converts negative dentries to `-ENOENT`, optionally dropping disposable negative dentries.
- `ovl_lookup_single()` handles one path element in one real layer, applying casefold checks, whiteout detection, metacopy detection, opaque/xwhiteout handling, redirect extraction, and trap checks.
- `ovl_lookup_layer()` resolves either a simple name or an absolute redirected path component by component.
- `ovl_lookup_data_layers()` searches data-only lower layers for a regular-file lowerdata target.
- `ovl_check_origin_fh()` scans lower layers for a decodable origin file handle.
- `ovl_verify_origin_xattr()` and `ovl_verify_set_fh()` compare or set stored origin/upper file-handle xattrs.
- `ovl_verify_index()`, `ovl_lookup_index()`, `ovl_get_index_name*()`, and `ovl_get_index_fh()` implement index-directory lookup and validation.
- `ovl_lookup_layers()` is the core overlay lookup algorithm.
- `ovl_lookup()` is the VFS inode operation entry point.
- `ovl_verify_lowerdata()` performs lazy lowerdata lookup and optional fs-verity validation.
- `ovl_lower_positive()` checks whether an overlay dentry has a positive lower-layer object.

## Lookup Flow

`ovl_lookup()` rejects names longer than the effective maximum component length, initializes lookup state, enters overlay creator credentials, and calls `ovl_lookup_layers()`.

`ovl_lookup_layers()` first searches the upper parent if an upper exists. A positive upper may provide origin metadata, metacopy state, and redirects. If an absolute upper redirect is found, lower lookup restarts from the root lower stack.

The lower traversal walks layer-by-layer from top to bottom. Each candidate lookup rejects unsupported dentries, casefold inconsistencies, whiteouts, trap inodes, and invalid metacopy states. `overlay.opaque=y` stops further lower lookup; `overlay.opaque=x` marks a directory that may contain xwhiteout files. Redirects can rewrite the lookup name and may restart lookup from the root stack.

For metacopy files, only the top metadata object is kept in the lower stack; lookup must eventually find a real data-bearing lower file. When data-only layers are configured and the metacopy redirect is absolute, the lowerdata lookup can be deferred by appending an empty lowerdata slot and storing the redirect string in the overlay inode.

After upper/lower discovery, the code verifies origins when needed, looks up index entries when indexing is enabled, allocates an `ovl_entry`, initializes dentry flags, and calls `ovl_get_inode()`.

## Index And Origin Invariants

Index names are hex-encoded lower origin file handles. Directory index entries carry `overlay.upper` pointing to the real upper directory; non-directory index entries are hardlinks to upper inodes. Index verification rejects malformed names, stale origins, wrong file types, bad whiteouts, orphan entries, and mismatched upper/origin relationships.

Origin mismatch handling is intentionally nuanced. Stale lower handles can be treated as unknown in compatibility paths, but index and NFS export paths require stronger verification to avoid aliasing distinct lower objects into the same overlay inode identity.

## Dependencies And Integration

This file depends on:

- `overlayfs.h` and `ovl_entry.h` for feature predicates, private structures, xattr IDs, and file-handle formats.
- `util.c` for xattr helpers, path accessors, whiteout checks, metacopy helpers, lowerdata publication, fs-verity validation, and credential override.
- `super.c` for mount-time feature choices and layer construction.
- `inode.c` for overlay inode lookup/creation, trap inodes, and nlink helpers.
- `readdir.c` through shared whiteout/xwhiteout and index cleanup semantics.
- VFS/exportfs APIs such as `lookup_one_unlocked()`, `vfs_path_lookup()`, `exportfs_decode_fh()`, and dentry revalidation flags.

## Risk Notes

- Redirect following is security-sensitive because it resembles symlink traversal into lower layers without normal path permission checks; `ovl_check_follow_redirect()` enforces feature gating.
- Index/origin file handles are consistency-critical for hardlinks, NFS export, and stable inode identity.
- Lazy lowerdata publication relies on memory barriers in `ovl_dentry_set_lowerdata()` and `ovl_path_lowerdata()`.
- Casefold consistency is checked during lookup, but offline lower-layer changes can still invalidate assumptions.
- Data-only layer redirects require absolute paths and only accept regular files as lowerdata.
