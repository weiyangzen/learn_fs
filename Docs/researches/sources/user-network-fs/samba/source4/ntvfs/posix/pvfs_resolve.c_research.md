# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_resolve.c

Purpose: `pvfs_resolve.c` converts client CIFS paths into validated POSIX paths and populated `struct pvfs_filename` objects. It centralizes path syntax checks, case-insensitive lookup, short-name lookup, stream parsing, wildcard handling, stat refresh, open-handle path refresh after rename, and parent resolution.

Important APIs, types, and functions: Public functions are `pvfs_resolve_name`, `pvfs_resolve_partial`, `pvfs_resolve_name_fd`, `pvfs_resolve_name_handle`, and `pvfs_resolve_parent`. Helpers include `component_compare`, `pvfs_case_search`, `parse_stream_name`, `pvfs_unix_path`, and `pvfs_reduce_name`.

Control flow: `pvfs_resolve_name` allocates `pvfs_filename`, strips stream support if the filesystem lacks named streams, rejects leading slash under SMB2, runs `pvfs_unix_path`, optionally reduces repeated separators or dot-dot syntax, and then either validates wildcard parent existence or stats/case-searches the final path. `pvfs_case_search` breaks the path into components beneath the share root, rejects reserved DOS names, consults the mangled-name cache, tries exact stat first, then scans directories case-insensitively. `pvfs_resolve_name_fd` refreshes stat data from fd or path and rejects dev/inode changes. `pvfs_resolve_name_handle` also consults the open database for renamed open files.

State and persistence behavior: Resolution itself is transient, but it reads persisted DOS metadata through `pvfs_fill_dos_info`, stream indexes through that path, and open-db path/write-time state for open handles. `allow_override` defaults false and follows the resolved name.

Dependencies and integration points: It depends on short-name mangling, stream metadata, `pvfs_fill_dos_info`, POSIX `stat`/directory scanning, protocol version, filesystem capability flags, and open-db path lookup. Nearly every other PVFS operation consumes its `pvfs_filename` output.

Risks: Path parsing is security-critical. Incorrect dot-dot reduction, separator handling, stream colon parsing, case-insensitive search, or dev/inode identity checks can cause path traversal or race issues. Stream IDs are hashes. SMB2 path syntax differs from SMB1.

Test signals: Cover illegal characters, control characters, repeated separators, dot and dot-dot components, leading SMB2 slashes, wildcards only in final component, reserved names, mangled short-name lookup, case-insensitive filesystems, stream names with `:$DATA`, and fd identity races.
