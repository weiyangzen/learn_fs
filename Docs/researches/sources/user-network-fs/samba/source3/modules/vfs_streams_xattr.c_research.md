# sources/user-network-fs/samba/source3/modules/vfs_streams_xattr.c

## Purpose

`vfs_streams_xattr.c` implements NTFS-style named streams by storing stream contents in extended attributes on the base file. It advertises `FILE_NAMED_STREAMS`, creates fake file descriptors for stream opens, derives stream stat metadata from the base file plus stream xattr content, and implements stream I/O by reading and rewriting xattr values.

## Important APIs, Types, And Functions

`struct streams_xattr_config` stores the primary xattr prefix, extension xattr prefix, maximum extents, and whether to persist `:$DATA` in raw stream names. `struct stream_io` is attached as an FSP extension for alternate-stream handles and caches base path, xattr names, raw stream name, owning `fsp`, and handle pointer.

Large stream support is implemented by `fgetxattr_multi()`, `fsetxattr_multi()`, and `fremovexattr_multi()`. The anchor xattr stores stream data plus a marker byte; marker zero means all data fits in the anchor, and nonzero marker values identify how many extension xattrs exist. `streams_xattr_ext_name()` builds primary and extent names. `streams_xattr_get_name()` parses `:<stream>[:$DATA]` names, honors `store_stream_type`, and builds raw and full xattr names.

VFS hooks cover connect, open/close, stat/fstat/lstat/fstatat, pread/pwrite and async wrappers, unlink, stream rename, truncate, fallocate, stream enumeration, fsync, lock/sharemode/lease/fcntl behavior, chmod/chown no-ops for streams, and xattr operations on stream FSPs.

## Control Flow

Connect reads `streams_xattr:prefix`, `streams_xattr:ext_prefix`, `streams_xattr:store_stream_type`, and `streams_xattr:max xattrs per stream`, then stores config on the VFS handle. Open passes non-stream paths through. For named streams it rejects unsupported resolution flags, resolves the xattr name, reads the existing value, creates or truncates an empty one-byte xattr when needed, allocates a fake fd, and attaches `stream_io` to the stream FSP.

Reads fetch the full xattr-backed stream into memory, subtract the marker byte from the logical length, and copy the requested range. Writes fetch the existing value, grow/zero-fill if needed, copy the new bytes, and write the complete value back across anchor and extent xattrs. Truncate resizes the value and rewrites it. Rename copies the source xattr payload to the destination with optional `XATTR_CREATE`, then removes the source. Enumeration lists xattr names, filters private Samba attributes, selects names with the configured prefix, reads values, and emits `stream_struct` entries.

## State And Persistence

Stream bytes persist as xattrs on the base file. Logical empty streams still consume a one-byte value because xattrs cannot represent zero-length payloads in this implementation. Large streams can span the anchor plus up to `max_extents` extension xattrs, with stale extension cleanup attempted when shrinking. Per-open transient state is held in the FSP extension and rechecked if `fsp->fsp_name` changes.

## Dependencies And Integration Points

The module depends on Samba VFS xattr operations, fake fd helpers, FSP extensions, `hash_inode()` for synthetic stream inode values, `tevent` async request wrappers, `get_ea_names_from_fsp()`, `samba_private_attr_name()`, and share parameter helpers. It is built as `vfs_streams_xattr`; selftest references include `samba3.blackbox.delete_stream` with `acl_streams_xattr` and `vfs.streams_xattr` torture runs.

## Risks And Edge Cases

The implementation rewrites whole streams on each write, so large streams are expensive and can hit xattr size limits. If an extent write fails after the anchor was updated, later reads can return short data when missing extents are encountered. Fsync for stream handles is effectively a no-op because there is no pathname-based sync in this layer and no direct basefile handle in that callback. Stream locks are mostly accepted locally rather than mapped to byte-range locks on a durable backing object. The source also contains suspicious implementation details: `SMB_VFS_HANDLE_SET_DATA()` names `struct stream_xattr_config` instead of `struct streams_xattr_config`, and some `tevent_req_nomem()` calls appear to pass arguments in the wrong order in pass-through async paths.

## Test Signals

Tests should cover one-byte empty streams, create/open/truncate/read/write/rename/unlink, stream names containing colons under fruit native encoding, multi-extent streams near `smbd max xattr size`, shrinking from multi-extent to short streams, enumeration filtering of Samba private attributes, fake-fd close behavior, and failure recovery after partial extent writes. Existing `vfs.streams_xattr` and delete-stream selftests are directly relevant.
