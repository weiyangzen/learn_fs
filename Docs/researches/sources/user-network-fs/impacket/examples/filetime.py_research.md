# sources/user-network-fs/impacket/examples/filetime.py

## Purpose

`filetime.py` is an SMB timestamp inspection and modification utility. It mimics `stat` and `touch` behavior for remote files or directories by opening an SMB path, querying basic file information, and optionally setting selected Windows FILETIME fields. It supports NTLM, hashes, Kerberos, AES keys, explicit ports, target IP override, DC IP, and optional post-write validation.

## Important APIs, Types, and Functions

`FileTimes` is a dataclass containing `creation_time`, `last_access_time`, `last_write_time`, and `change_time` as Windows FILETIME integers. `pretty_repr()` converts populated fields with `FTtoPOSIX()` and `datetime.fromtimestamp()`, rendering `None` as `N/A`.

`filetime_query(connection, tid, fid)` chooses `SMBQueryFileBasicInfo` for SMB1 dialects and `FILE_BASIC_INFORMATION` for SMB2/3, then returns a `FileTimes` object. `filetime_set(connection, tid, fid, filetimes)` performs the inverse, building `SMBSetFileBasicInfo` or `FILE_BASIC_INFORMATION` and calling `SMBConnection.setInfo()`. `main()` owns CLI parsing, credential handling, SMB login, tree connect, file open, query/set, validation, and cleanup.

## Control Flow

The CLI requires `target`, `share`, `path`, and an action subcommand: `stat` or `touch`. For `touch`, the caller must provide exactly one source of new times: `--reference <share> <path>` to copy timestamps from another SMB object, or `--timestamp` parsed by `datetime.fromisoformat()`. The `-c/-a/-w/-m` flags decide which fields are written; unselected fields are reset to `None`, which `filetime_set()` serializes as zero so the server leaves them unchanged.

After parsing credentials with `parse_target()`, the script creates an `SMBConnection`, authenticates with either `kerberosLogin()` or `login()`, optionally opens a reference object, opens the target object with minimal access rights, performs `stat` or `touch`, and closes handles and tree connections in `finally` blocks.

## State and Persistence Behavior

State is mostly local CLI and connection state. The only persistent external effect is a remote SMB metadata update through `setInfo()`. The script does not create local files. It keeps selected timestamps as in-memory FILETIME values and depends on the SMB server preserving unspecified timestamp fields when zero is supplied in a set-basic-info request.

## Dependencies and Integration Points

The script integrates with Impacket `smbconnection`, SMB1 structures from `impacket.smb`, SMB2/3 structures from `impacket.smb3` and `impacket.smb3structs`, `parse_target()`, and the shared example logger. It is an executable example rather than a library API, but its helper functions could be reused by other SMB tools.

## Risks and Edge Cases

The file contains duplicate import blocks, including repeated `argparse`, `smbconnection`, and SMB constants, which is harmless but noisy. The `finally` blocks call `closeFile()` and `disconnectTree()` even if `connectTree()` or `openFile()` failed before assigning IDs, so connection errors can mask the original exception with an unbound local error. Timestamp parsing uses local timezone semantics when `fromisoformat()` returns a naive datetime. The `None -> 0` update behavior is protocol-dependent and should be verified against SMB servers before assuming fields are untouched. Directory support relies on `creationOption=0`; server implementations may vary.

## Test Signals

Useful tests mock `SMBConnection` dialects and assert that `filetime_query()` and `filetime_set()` select the expected info classes and field names for SMB1 versus SMB2. Integration tests should cover `stat`, timestamp-based `touch`, reference-based `touch`, validation mode, Kerberos/hash/no-password paths, malformed timestamp input, missing action, and failure during open/close cleanup.
