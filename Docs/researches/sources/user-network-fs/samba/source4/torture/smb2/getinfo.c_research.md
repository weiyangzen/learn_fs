# sources/user-network-fs/samba/source4/torture/smb2/getinfo.c

## Purpose

This file defines the SMB2 getinfo torture suite. It verifies SMB2 file information, filesystem information, security information buffer sizing, normalized-name handling, granted-access reporting, and per-information-level access requirements. The suite exercises both ordinary query paths through typed wrappers such as `smb2_getinfo_file()` and raw `SMB2_GETINFO` buffer behavior through `smb2_getinfo()`.

## Important APIs, Types, And Tables

The static `file_levels[]` table lists file information classes tested against both a file and a directory, including basic, standard, internal, EA, access, position, mode, alignment, all, alternate name, stream, compression, network open, attribute tag, all EAs, SMB2 all information, and security descriptor queries.

The static `fs_levels[]` table lists filesystem information classes: volume, size, device, attribute, quota, full size, object id, and sector size. Each row stores the queried `union smb_fsinfo` and status.

`file_levels_access[]` maps information classes to access behavior. It distinguishes classes that are effectively unrestricted with a minimal synchronize-style open from classes that require `SEC_FILE_READ_ATTRIBUTE`, `SEC_FILE_READ_EA`, or `SEC_STD_READ_CONTROL`.

Key functions are:

- `torture_smb2_fileinfo()` creates a test file and directory, runs `torture_smb2_all_info()`, then queries every file info class for both handles.
- `torture_smb2_fileinfo_grant_read()` verifies `RAW_FILEINFO_ALL_INFORMATION` reports granted access exactly as opened when the handle has execute plus read-attribute access.
- `torture_smb2_fileinfo_normalized()` verifies `RAW_FILEINFO_NORMALIZED_NAME_INFORMATION` for mixed-case paths, streams, default data streams, and SMB dialect support.
- `torture_smb2_fsinfo()` queries every filesystem info class against the root handle.
- `torture_smb2_buffercheck_err()` is the common raw-buffer validator for fixed-size minimum, overflow, and exact-size behavior.
- `torture_smb2_qfs_buffercheck()`, `torture_smb2_qfile_buffercheck()`, and `torture_smb2_qsec_buffercheck()` validate buffer-length error codes for filesystem, file, and security getinfo.
- `torture_smb2_getfinfo_access()` verifies expected access-denied and success results for each file information class in `file_levels_access[]`.

## Control Flow

`torture_smb2_getinfo()` is the "complex" entry point. It connects, deletes stale `FNAME` and `DNAME`, creates complex test file and directory data including alternate streams, and then delegates to `torture_smb2_fileinfo()`.

`torture_smb2_fileinfo()` opens a test file and directory, runs a broad all-info helper for each, and iterates `file_levels[]`. Before querying security descriptors it sets `secinfo_flags = 0x7`; before querying all EAs it sets `SMB2_CONTINUE_FLAG_RESTART`. Each query is expected to return OK.

The normalized-name test constructs a nested mixed-case directory tree and stream paths. It first checks the root handle. Protocols below SMB 3.1.1 must return `NT_STATUS_NOT_SUPPORTED`; servers that do not implement the feature may skip. Once supported, it creates and reopens each path in lower and upper case, then asserts that normalized names return the canonical original case and strip default `:$DATA` suffixes where expected. It also opens a second connection capped at SMB 3.0.2 and verifies normalized-name queries are not supported there.

The buffer-check tests first issue a large-output query to capture the full response, then loop every output length from zero through the full length. Lengths below the fixed structure minimum must return `NT_STATUS_INFO_LENGTH_MISMATCH`; lengths at or above the fixed minimum but below the full response must return `STATUS_BUFFER_OVERFLOW`; the exact full length must return `NT_STATUS_OK`. The security buffer test is special: zero and one byte both must return `NT_STATUS_BUFFER_TOO_SMALL`.

`torture_smb2_getfinfo_access()` loops `file_levels_access[]` twice per row. It first opens with the listed unrestricted/minimal access and expects either OK or access denied depending on the row. It then reopens with the required access and expects the query to succeed.

## State And Persistence Behavior

The suite creates deterministic names `testsmb2_file.dat`, `testsmb2_dir`, `bufsize.txt`, and `torture_smb2_getfinfo_access`, plus a mixed-case nested tree rooted at `torture_dIr1N` for normalized-name checks. It uses `smb2_deltree()` to clear stale paths before setup and after the access test. Some helper-created handles are closed inline, but the tests primarily rely on short-lived torture connections and talloc lifetimes.

The normalized-name test intentionally persists multiple simultaneously open handles to the same objects through differently cased names. This preserves enough state to compare server canonicalization across file, directory, stream, default stream, lower-case, and upper-case opens.

The query result tables store status and output unions statically for the duration of the process. They are test result storage rather than durable filesystem state.

## Dependencies And Integration Points

This file depends on Samba's SMB2 client library, `smbXcli_base` protocol helpers, `torture/torture.h`, `torture/smb2/proto.h`, and `torture/util.h`. It uses helper functions such as `torture_setup_complex_file()`, `torture_setup_complex_dir()`, `torture_smb2_testfile_access()`, `torture_smb2_get_allinfo_access()`, `smb2_util_roothandle()`, and `torture_smb2_open()`.

The suite is registered by `torture_smb2_getinfo_init()` under suite name `getinfo`, with tests `complex`, `fsinfo`, `qfs_buffercheck`, `qfile_buffercheck`, `qsec_buffercheck`, `granted`, `normalized`, and `getinfo_access`.

The normalized-name behavior integrates with SMB dialect negotiation through `smbXcli_conn_protocol()` and an explicit second connection with `options3_0.max_protocol = PROTOCOL_SMB3_02`. Filesystem buffer checks contain Samba-specific skips for info classes 6 and 11 when targeting Samba3 or Samba4.

## Risks And Edge Cases

The normalized-name test is sensitive to server support and dialect. It correctly skips unsupported implementations, but a failure after support is detected indicates subtle canonical-name, stream-name, or default-data-stream behavior. Case-insensitive filesystems, stream support, and server normalization policy all matter.

The buffer-size tests assume specific fixed-size minima for numeric info classes, noted in comments as lacking proper defines. Changes in parser structures, protocol constants, or server response layout can require updating these hard-coded minima.

Some raw buffer comparisons are intentionally not performed for overflow responses because variable-length fields and reserved bytes are difficult to compare. The test validates status-code behavior, not byte-for-byte overflow payload shape.

The access tests rely on expected distinctions between unrestricted info classes and classes requiring read attributes, read EAs, or read control. Server-side permission model changes can affect these statuses and should be reviewed against MS-SMB2 semantics rather than treated as generic failures.

## Test Signals

Passing signals include OK statuses for all listed file and filesystem info levels, exact granted-access values for execute/read-attribute opens, correct normalized names for lower/upper/mixed-case and stream paths, expected `NT_STATUS_NOT_SUPPORTED` below SMB 3.1.1, correct buffer-length status transitions, and access denied only for classes queried without their required rights.

High-value failure signals include security descriptor queries succeeding without `SEC_STD_READ_CONTROL`, all-EA queries succeeding without `SEC_FILE_READ_EA`, normalized names returning the client-supplied casing rather than canonical casing, full-size buffer queries returning overflow, and undersized raw getinfo queries returning a generic failure instead of the expected SMB2 length status.
