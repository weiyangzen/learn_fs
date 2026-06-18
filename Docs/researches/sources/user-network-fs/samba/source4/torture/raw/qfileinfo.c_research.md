# sources/user-network-fs/samba/source4/torture/raw/qfileinfo.c

## Purpose
This file implements raw SMB file-information torture tests. It exercises a broad matrix of `RAW_FILEINFO_*` and path-info levels against both a normal disk file and an IPC named pipe, then checks that equivalent protocol information levels agree on timestamps, size, allocation, attributes, names, streams, EAs, file IDs, position, and device-specific behavior. The exported entry points are `torture_raw_qfileinfo()` and `torture_raw_qfileinfo_pipe()`.

## Important APIs, Types, And Functions
The central state is the static `levels[]` table. Each row names an SMB file-info level, records whether it is handle-only or path-only, declares required capabilities such as `CAP_UNIX`, stores expected IPC failure behavior, and keeps both handle (`fnum_finfo`) and path (`fname_finfo`) query results.

`torture_raw_qfileinfo_internals()` drives the suite. It calls `smb_raw_fileinfo()` for handle-capable levels and `smb_raw_pathinfo()` for path-capable levels, then uses helper lookups `fnum_find()` and `fname_find()` plus comparison macros to validate relationships across levels. `dos_nt_time_cmp()` tolerates DOS two-second timestamp resolution. `torture_raw_qfileinfo()` creates a complex disk file with `create_complex_file()`, while `torture_raw_qfileinfo_pipe()` opens `\lsass` on IPC using `RAW_OPEN_NTCREATEX`.

## Control Flow
The internal test first probes every level and records NTSTATUS results. It then filters by negotiated capabilities and IPC/non-IPC mode to distinguish unsupported levels from real failures. After that broad liveness check, it performs consistency checks: aliases such as `BASIC_INFO` versus `BASIC_INFORMATION`, `STANDARD_INFO` versus `STANDARD_INFORMATION`, and `ALL_INFO` versus `ALL_INFORMATION`; NT versus DOS timestamp encodings; size and allocation values; attributes; file names and alternate names; stream metadata; EA size accounting; and handle/path agreement for file ID, position, mode, alignment, attributes, and reparse tags.

If alternate-name information is available, the test closes and reopens the file by its short name to verify the returned name is usable. If stream information is missing or empty, stream checks are skipped rather than failing the whole suite. The public disk-file test closes and unlinks the file; the pipe test only closes the pipe handle.

## State And Persistence Behavior
The disk-file case creates `\torture_qfileinfo.txt` and removes it at the end. The IPC case opens a named pipe and does not create filesystem state. The `levels[]` array is static and mutable: every run overwrites each row's status and result unions. That is acceptable inside the single test flow but means the table is not reentrant or thread-local. Handle position is explicitly checked but most queries are metadata-only.

## Dependencies And Integration Points
This file depends on Samba's raw SMB client API (`smb_raw_fileinfo`, `smb_raw_pathinfo`, `smb_raw_open`), torture helpers (`create_complex_file`, `torture_assert_ntstatus_ok`, `torture_comment`), negotiated transport capabilities, talloc allocation, and wire string validation through `wire_bad_flags()`. It is registered by `raw.c` as `qfileinfo` and `qfileinfo.ipc`.

## Risks And Edge Cases
The static table retains results between probes, so future parallelization or nested invocation would need isolation. Some compatibility behavior is intentionally loose: unsupported or unimplemented levels may warn and continue, and stream checks are skipped when stream metadata is absent. The IPC branch has distinct expected statuses (`INVALID_DEVICE_REQUEST`, `ACCESS_DENIED`, `INVALID_PARAMETER`, `delete_pending` expectations), so changes in named-pipe semantics can fail this test even when normal files pass. Timestamp checks depend on resolution conversions, and alternate-name reopening can mutate the handle under test.

## Test Signals
Strong pass signals are all capability-advertised levels returning expected statuses and all alias/value comparisons matching. Failures print the level name, field names, actual and expected values, source line, and NTSTATUS. More than 35 broken levels triggers an immediate torture failure to avoid cascading noise.
