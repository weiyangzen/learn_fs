# sources/user-network-fs/cifs-utils/smbinfo

## Purpose
`smbinfo` is a Python 3 command-line multiplexer for querying SMB-specific file, filesystem, snapshot, quota, security descriptor, compression, key, and tcon/session information through Linux CIFS ioctls.

## Important APIs, types, and functions
The script defines ioctl constants for `CIFS_QUERY_INFO`, `CIFS_ENUMERATE_SNAPSHOTS`, `CIFS_DUMP_KEY`, `CIFS_DUMP_FULL_KEY`, and `CIFS_GET_TCON_INFO`. `QueryInfoStruct` centralizes packing the query-info header and input/output buffer. Formatting helpers include `flags_to_str`, `type_to_str`, `win_to_datetime`, `guid_to_str`, and `bytes_to_hex`. Domain parsers include `SnapshotArrayStruct`, `SID`, `ACE`, `KeyDebugInfoStruct`, `FullKeyDebugInfoStruct`, and `SmbMntTconInfoStruct`. Subcommands cover file access/alignment/all/basic/EA/fs-size/internal/mode/position/standard/stream info, FSCTL object ID, compression get/set, snapshots, quota, secdesc, keys, and tcon info.

## Control flow
`main` builds an argparse subcommand table and dispatches to `cmd_*` handlers. Most handlers open the supplied file, instantiate a query struct with SMB info type/class/flags, call the ioctl, and hand the returned byte buffer to a `print_*` decoder. Snapshot listing uses a two-pass ioctl to discover and then fetch the array. Key dumping first tries the newer full-key ioctl and falls back to the older fixed-size key dump.

## State and persistence behavior
Most subcommands are read-only. `setcompression` changes remote file compression state through an FSCTL passthrough. `keys` exposes session material for network trace decryption and prints secrets to stdout.

## Dependencies and integration points
It depends on Python 3, Linux-specific CIFS ioctls, cifs.ko support for the requested info classes, and SMB server capabilities. It integrates with other cifs-utils ACL/quota tools by decoding the same SIDs, ACEs, quota records, and security descriptors.

## Risks
Manual binary parsing lacks response-length checks and can raise `struct.error` on short buffers. Some file descriptors are not closed on every path. `win_to_datetime` uses local timezone conversion, which may surprise users comparing SMB UTC values. `SID.subauth` stores one-element tuples due to missing `[0]`, so SID string formatting may be wrong for security descriptor output. `keys` can leak sensitive session keys and should remain privileged/debug oriented.

## Test signals
Add synthetic-buffer tests for each `print_*` parser, CLI parser tests for every subcommand, and live CIFS integration tests gated on a mounted share. Include negative tests on non-CIFS files, short ioctl responses, snapshot arrays, secdesc SID formatting, compression set/get, and key-dump permission failures.
