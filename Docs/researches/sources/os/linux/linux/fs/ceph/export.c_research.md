# File Research: sources/os/linux/linux/fs/ceph/export.c

## Role

`export.c` implements Linux `export_operations` for CephFS, enabling exportfs/NFS-style file handles to encode/decode Ceph inodes, snapped inodes, parents, and names. It bridges VFS export callbacks to Ceph MDS lookup operations and handles Ceph snapshot namespace special cases.

## File Handle Formats

Packed on-wire handle structs:

- `struct ceph_nfs_fh { u64 ino; }`: basic non-snapped inode handle.
- `struct ceph_nfs_confh { u64 ino, parent_ino; }`: non-snapped handle with parent.
- `struct ceph_nfs_snapfh { u64 ino, snapid, parent_ino; u32 hash; }`: snapped inode handle with parent and dentry hash context.

Lengths are expressed in `u32` units for exportfs callbacks.

## Encoding

- `ceph_encode_fh()` chooses normal or snapped encoding based on `ceph_snap(inode)`.
- Normal handles return `FILEID_INO32_GEN` or `FILEID_INO32_GEN_PARENT` even though Ceph stores 64-bit inode fields in the raw payload.
- `ceph_encode_snapfh()` returns `FILEID_BTRFS_WITH_PARENT` for snapped inodes. For non-snapdir snapped inodes, it tries to find a dentry alias, records the parent inode and `ceph_dentry_hash()`, and falls back only for directories where parent can be represented by self.
- If the caller-provided buffer is too small, the functions set the required length and return `FILEID_INVALID`.

## Decoding Inodes and Dentries

- `__lookup_inode()` looks for a head inode in the local cache with `ceph_find_inode()`, otherwise issues MDS `LOOKUPINO`. Reserved vinos are `-ESTALE`.
- `ceph_lookup_inode()` wraps `__lookup_inode()` and rejects unlinked inodes with `i_nlink == 0`.
- `__fh_to_dentry()` obtains an inode, refreshes link caps with `ceph_do_getattr(..., CEPH_CAP_LINK_SHARED)`, rejects unlinked closed files as stale, and returns `d_obtain_alias()`.
- `__snapfh_to_dentry()` decodes snapped and snapdir handles. It can return either target or parent, includes snapid/parent/hash in `LOOKUPINO`, maps head inode to snapdir where needed, and treats unlinked snapped directories with `d_obtain_root()` to avoid further disconnected-parent walks.

## Parent Resolution

- `__get_parent()` issues MDS `LOOKUPPARENT`, either from a child inode or raw ino, then returns `d_obtain_alias()` for the parent inode.
- `ceph_get_parent()` special-cases snapped dentries: non-directory snapped children are rejected, snapped directories resolve through the head inode's snapdir, and unlinked directories use `d_obtain_root()`.
- `ceph_fh_to_parent()` decodes either snapped handles with `__snapfh_to_dentry(..., true)` or connected normal handles. If `LOOKUPPARENT` returns `-ENOENT`, it falls back to the encoded parent ino.

## Name Resolution

- `ceph_get_name()` issues MDS `LOOKUPNAME` to recover a child's name under a parent for non-snapped inodes. It decodes encrypted names via `ceph_fname_to_usr()` using the primary and alternate names from the MDS reply.
- `__get_snap_name()` handles snapped namespace names:
  - snapdir under head inode returns the configured `snapdir_name`,
  - snapped children under a snapdir are found by paging through `LSSNAP` readdir replies until a matching snapid is found.

## Export Operations

`ceph_export_ops` wires:

- `.encode_fh = ceph_encode_fh`
- `.fh_to_dentry = ceph_fh_to_dentry`
- `.fh_to_parent = ceph_fh_to_parent`
- `.get_parent = ceph_get_parent`
- `.get_name = ceph_get_name`

## Dependencies and Semantics

This file depends on `dir.c` for `ceph_dentry_hash()` and snapdir semantics, MDS client request operations for `LOOKUPINO`, `LOOKUPPARENT`, `LOOKUPNAME`, and `LSSNAP`, and crypto helpers for encrypted filename presentation.

Stale detection is conservative: reserved vinos, shutdown inodes, missing MDS targets, unlinked closed files, unsupported snapped lookup, and malformed handle lengths all return stale/error/null results appropriate to exportfs.
