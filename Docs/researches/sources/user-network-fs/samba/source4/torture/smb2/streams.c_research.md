# sources/user-network-fs/samba/source4/torture/smb2/streams.c

## Purpose
`streams.c` implements the `smb2.streams` torture suite for SMB2 alternate data stream behavior. It is a protocol conformance and regression collection for named streams on files and directories, including stream creation, lookup, stream list enumeration, delete-on-close, share-mode interaction, stream name parsing, case-insensitive stream lookup, stream rename semantics, create disposition effects, metadata propagation between base file and streams, and a Samba inherit-permissions crash regression.

## Important APIs, Types, and Functions
The suite entry point is `torture_smb2_streams_init()`, which registers tests named `dir`, `io`, `sharemodes`, `names`, `names2`, `names3`, `rename`, `rename2`, `create-disposition`, `attributes1`, `attributes2`, `delete`, `zero-byte`, and `basefile-rename-with-open-stream`. Local helpers include `check_stream()`, which opens `<base>:<stream>` and optionally verifies stream data, `check_stream_list()`, which queries `RAW_FILEINFO_STREAM_INFORMATION` and compares sorted stream names, `create_file_with_stream()`, `open_stream()`, and `check_metadata()`.

The file uses `struct smb2_tree`, `struct smb2_handle`, `struct smb2_create`, `struct smb2_read`, `union smb_open`, `union smb_fileinfo`, and `union smb_setfileinfo`. Most assertions use local `CHECK_STATUS`, `CHECK_VALUE`, `CHECK_NTTIME`, `CHECK_STR`, and `CHECK_CALL_HANDLE` macros that fail through the torture context and jump to cleanup.

## Control Flow
Every test creates a clean `teststreams` directory with `torture_smb2_testdir()` after removing prior contents with `smb2_deltree()` or `smb2_util_unlink()`. The tests then build SMB2 create/open or setinfo requests against path forms such as `file:stream`, `file:stream:$DATA`, `file::$DATA`, and invalid variants.

`test_stream_dir()` verifies that directory stream opens fail with the expected not-a-directory or file-is-directory statuses. `test_stream_io()` creates streams on nonexistent and existing base files, writes and rewrites data, checks default and named stream list entries, and verifies deletion through unlink and delete-on-close. `test_zero_byte_stream()` asserts that a zero-length named stream is still returned in stream enumeration.

`test_stream_sharemodes()` and `test_stream_delete()` exercise stream-specific sharing and delete behavior: different streams can avoid share conflicts, the same stream conflicts, an open stream without `FILE_SHARE_DELETE` blocks deleting the base file, and delete-pending behavior blocks name-based access until open stream handles close. `test_stream_names()`, `test_stream_names2()`, and `test_stream_names3()` cover unusual characters, invalid stream type suffixes, wildcard-like stream names, stream metadata queries, stream rename collisions, control-character rejection, and case-insensitive stream access when the filesystem advertises case-sensitive search support. `test_stream_rename()` and `test_stream_rename2()` focus on SMB1-style and SMB2-style rename information buffers for stream-to-stream and stream-to-default-stream renames.

`test_stream_create_disposition()` verifies that base-file `OVERWRITE`, `OVERWRITE_IF`, and `SUPERSEDE` remove named streams while stream-level overwrite preserves the stream set. `test_stream_attributes1()` and `test_stream_attributes2()` check that stream timestamp and attribute updates are reflected on the base file where Windows-compatible semantics require it, and that creation time is not accidentally refreshed by writes. `test_basefile_rename_with_open_stream()` uses a second SMB2 connection and expects renaming the base file to fail while a stream is open. `test_stream_inherit_perms()` reads and extends a directory security descriptor, writes the DACL back, then creates a stream under the directory to trigger bug 15695 coverage.

## State and Persistence Behavior
The tests mutate a live SMB share under `teststreams` and a few temporary top-level names. Persistent state under test includes named streams, stream data, open-handle share tables, delete-pending state, file metadata, security descriptors, and directory entries. Local state is stack or talloc-scoped, with explicit handle cleanup in `done` blocks and tree cleanup at test end. Some tests skip or adjust behavior based on torture settings such as `samba3` and `samba4`.

## Dependencies and Integration Points
This file depends on Samba's SMB2 client calls (`smb2_create`, `smb2_read`, `smb2_getinfo_file`, `smb2_setinfo_file`), SMB2 torture helpers from `torture/smb2/proto.h`, talloc, stream sorting via `TYPESAFE_QSORT`, locale helpers for character tests, and security descriptor helpers. It integrates with the broader `TORTURE_SMB2` module through `torture_smb2_streams_init()`.

## Risks
The suite encodes exact Windows-compatible ADS behavior, so expected statuses can be brittle across Samba backends, non-NTFS-like filesystems, or target profiles. Timing and metadata propagation checks can be sensitive to filesystem timestamp granularity. The tests are destructive under their test directory and assume stream syntax and delete-pending semantics are implemented consistently by the server.

## Test Signals
Failures are reported as mismatched `NTSTATUS`, unexpected stream names or counts, bad stream data, incorrect metadata values, unexpected share-mode acceptance, missing delete-pending behavior, invalid rename outcomes, or security descriptor/permission inheritance regressions.
