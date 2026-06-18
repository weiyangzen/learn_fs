# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_xattr.c

## Purpose
Implements Solaris extended attributes for SMBFS by representing SMB named streams as files inside a fake XATTR directory vnode.

## Core Model
- SMB named streams are not real directories, but Solaris expects an xattr directory.
- SMBFS fakes an xattr directory by creating an `smbnode` whose remote path appends `:` to the parent path.
- Children of that fake directory represent named streams.
- Path construction rules:
  - Normal paths use `\`.
  - Entering the fake XATTR directory adds one `:`.
  - Children under the fake XATTR directory add no extra separator, ensuring exactly one colon before the stream name.

## Key Functions
- `smbfs_get_xattrdir(...)`
  - Rejects recursive xattrs under xattrs.
  - Creates/finds the fake xattr directory node with `:` suffix.
  - Marks vnode as `VDIR | V_XATTRDIR` and node as `N_XATTR`.
- `smbfs_xa_parent(...)`
  - For an XATTR directory, trims the trailing colon to find the real parent.
  - For an XATTR file, trims after the first colon to find the fake xattr directory.
- `smbfs_xa_exists(...)`
  - Lists streams and returns true if at least one named stream exists.
- `smbfs_xa_getfattr(...)`
  - Returns fake directory attributes for `V_XATTRDIR`.
  - For stream files, looks up the stream name in the xattr directory and returns its attributes.
- `smbfs_xa_get_streaminfo(...)`
  - Resolves the real parent object and fetches stream information through SMB2 or SMB1.
  - Stores stream info in `ctx->f_mdchain` and marks EOF after one successful stream-info fetch.
- `smbfs_xa_findopen(...)`
  - Initializes an XATTR find context using `FileStreamInformation`.
- `smbfs_xa_findnext(...)`
  - Fetches stream info as needed and decodes entries with `smbfs_decode_dirent`.
  - Strips trailing `:$DATA`.
  - Skips the empty unnamed-data stream entry.
  - Applies case-insensitive filtering for single-name lookup.
- `smbfs_xa_findclose(...)`
  - Frees the find context name buffer.

## Important Interactions
- Depends on `smbfs_fullpath` suppressing separators for `N_XATTR`.
- Depends on SMB1/SMB2 stream info protocol helpers.
- Used by vnode lookup/pathconf/getattr/create logic to expose named streams through Solaris xattr APIs.
