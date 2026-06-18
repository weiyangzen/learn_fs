# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_streams.c

Purpose: `pvfs_streams.c` implements Windows alternate data streams on top of xattrs or the PVFS EADB backend. It maintains stream indexes, exposes stream information, and provides read/write/truncate/create/delete/rename behavior for stream data.

Important APIs, types, and functions: Public functions include `pvfs_stream_information`, `pvfs_stream_info`, `pvfs_stream_rename`, `pvfs_stream_create`, `pvfs_stream_delete`, `pvfs_stream_read`, `pvfs_stream_write`, and `pvfs_stream_truncate`. Helpers include `stream_name_normalise`, `stream_name_cmp`, `pvfs_stream_update_size`, and `pvfs_stream_load`.

Control flow: Stream names are normalized by dropping `:$DATA` suffixes. Querying stream information returns the default `::$DATA` stream plus xattr-indexed streams. `pvfs_stream_info` marks the default stream as always existing and searches the stream index for named streams. Create creates the per-stream xattr and adds a zero-size index entry. Reads load the stream blob, clamp to available bytes, and copy data. Writes load or create a blob, extend with zero fill as needed, save it, then update the stream index. Truncate resizes a blob and updates the index. Rename updates index names and handles overwrite rules; delete removes both the data xattr and index entry.

State and persistence behavior: Stream payloads are individual xattrs with `XATTR_DOSSTREAM_PREFIX`; stream metadata lives in the `XATTR_DOSSTREAMS_NAME` NDR xattr. Data can also be stored in the TDB EADB. Size and allocation values are persisted in the stream index and rounded through PVFS allocation rounding.

Dependencies and integration points: It uses xattr wrappers, NDR-generated xattr structures, allocation rounding, and is called by open, read, write, setfileinfo, qfileinfo, rename, unlink, and resolve paths.

Risks: Stream I/O loads whole blobs into memory. Filesystem xattr stream size limits differ from EADB limits. Case-insensitive stream lookup can require a second index scan. The default stream cannot be renamed over. Metadata and payload xattrs must remain consistent across failures.

Test signals: Cover stream create/open/read/write/sparse extension/truncate/delete, case-insensitive stream names, `:$DATA` normalization, stream information listing, overwrite rename, size-limit failures with and without EADB, and cleanup on delete-on-close.
