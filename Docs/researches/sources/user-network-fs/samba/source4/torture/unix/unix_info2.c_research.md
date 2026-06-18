# sources/user-network-fs/samba/source4/torture/unix/unix_info2.c

## Purpose
`unix_info2.c` tests the CIFS UNIX extension `SMB_QUERY_FILE_UNIX_INFO2` and related set/find operations. It verifies that file-info, path-info, and directory-search variants return consistent UNIX metadata and that `SMB_SFILEINFO_UNIX_INFO2` accepts or rejects file flag updates according to the server-advertised mask.

## Important APIs, Types, and Functions
The local `struct unix_info2` mirrors the UNIX_INFO2 fields: EOF, bytes, times, uid/gid, file type, device numbers, unique id, permissions, link count, create time, file flags, and flags mask. Important helpers are `connect_to_server()`, `check_unix_info2()`, `set_path_info2()`, `query_file_path_info2()`, `query_file_info2()`, `query_path_info2()`, `search_callback()`, `find_single_info2()`, `set_no_metadata_change()`, `verify_setinfo_flags()`, `create_file()`, `match_info2()`, and the exported `unix_torture_unix_info2()`.

## Control Flow
`connect_to_server()` opens an SMB1 client connection and sends `SMB_SET_CIFS_UNIX_INFO` through `smb_raw_trans2()` to enable UNIX capabilities such as POSIX ACLs, POSIX pathnames, fcntl locks, extended attributes, and POSIX path operations. `unix_torture_unix_info2()` unlinks any prior test file, creates `\smb_unix_info2.txt`, queries UNIX_INFO2 by file handle, queries it by path, compares the two, queries it through a `SMB_FIND_UNIX_INFO2` find-first search, compares again, then verifies flag-setting behavior.

`verify_setinfo_flags()` first reads the server's flags mask. It then iterates all 32 possible flag bits, sets `file_flags` to exactly one bit and `flags_mask` to include that bit, fills all unrelated metadata fields with no-change sentinels, and calls `set_path_info2()`. Bits included in the server mask must succeed and be observable afterward; unsupported bits must return `NT_STATUS_INVALID_PARAMETER`. Finally it verifies that a zero mask with all flags set is accepted as a no-op.

## State and Persistence Behavior
The test creates and deletes one file on the target share. It changes UNIX extension negotiation state on the SMB connection and temporarily changes file flags through UNIX_INFO2 setpathinfo. Cleanup closes the file handle, unlinks the file, closes the SMB connection, and frees the talloc context.

## Dependencies and Integration Points
The file uses SMB1 raw client APIs, Trans2, UNIX extension constants, command-line credentials, loadparm options, resolver/event contexts, and the generic torture assertion framework. It is registered by `unix.c` as `unix.info2`.

## Risks
The test requires a server implementing CIFS UNIX extensions; non-support or partial support will fail during negotiation or info levels. File flag behavior depends on backend filesystem capabilities, and the exhaustive 32-bit flag loop assumes unsupported flags are rejected exactly with `NT_STATUS_INVALID_PARAMETER`.

## Test Signals
Signals include successful UNIX extension negotiation, matching file/path/find metadata, valid `file_flags` constrained by `flags_mask`, accepted supported flag updates, rejected unsupported flag updates, and accepted no-op zero-mask updates.
