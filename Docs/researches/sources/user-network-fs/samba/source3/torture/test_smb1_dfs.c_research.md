# sources/user-network-fs/samba/source3/torture/test_smb1_dfs.c

## Purpose
This large smbtorture source is a raw SMB1 DFS behavior suite. It verifies how an SMB1 DFS share parses pathnames and search patterns, and how classic SMB1 commands behave when the apparent path includes DFS server/share components. The tests intentionally use low-level SMB1 request builders rather than the higher-level `cli_*` pathname wrappers because the target is server-side DFS path parsing and protocol compatibility, especially behavior observed against Windows.

The exported entry points are `run_smb1_dfs_paths`, `run_smb1_dfs_search_paths`, `run_smb1_dfs_operations`, and `run_smb1_dfs_check_badpath`.

## Important APIs, Types, And Functions
The shared helpers are `get_smb1_crtime()`, `smb1_crtime_matches()`, and `smb1_dfs_delete()`. They use `smb1cli_ntcreatex()`, `cli_qfileinfo_basic()`, `cli_nt_delete_on_close()`, and `smb1cli_close()` to identify objects by create time and clean up test artifacts through file handles.

Rename and hardlink coverage is split by protocol mechanism:
- `smb1_mv_send()/smb1_mv()` builds an `SMBmv` request.
- `smb1_setpathinfo_send()/smb1_setpathinfo()` sends `SMBtrans2` `TRANSACT2_SETPATHINFO` with `SMB_FILE_RENAME_INFORMATION` or `SMB_FILE_LINK_INFORMATION`.
- `smb1_ntrename_send()/smb1_ntrename()` builds `SMBntrename` with `RENAME_FLAG_RENAME` or `RENAME_FLAG_HARD_LINK`.
- `smb1_setfileinfo_send()/smb1_setfileinfo()` sends handle-based set-info data for rename/link levels.

Search coverage uses `smb1_findfirst()`, `calc_next_entry_offset()`, `get_filename()`, and `test_smb1_findfirst_path()` to issue a one-shot `TRANSACT2_FINDFIRST` and parse `SMB_FIND_FILE_BOTH_DIRECTORY_INFO` records.

Operation coverage includes raw wrappers and tests for `SMBunlink`, `SMBmkdir`, `SMBrmdir`, `NT_CREATE_ANDX`, `NT_TRANSACT_CREATE`, `SMBopenX`, `SMBopen`, `SMBcreate`, `SMBmknew`, `SMBgetatr`, `SMBsetatr`, `SMBcheckpath`, `SMBctemp`, and `TRANSACT2_QPATHINFO`.

## Control Flow
Every exported `run_*` function opens a torture connection, verifies both connection-level DFS support with `smbXcli_conn_dfs_supported()` and tree-connect DFS-share status with `smbXcli_tcon_is_dfs_share()`, then runs a set of low-level checks. If DFS support is absent, the test reports the server/share limitation and returns false rather than trying non-DFS behavior.

`run_smb1_dfs_paths()` starts with cleanup, constructs the official DFS root path as `\\<remote_name>\\<share>`, records its create time, and checks that many abbreviated or malformed server/share prefixes resolve to the share root. It verifies expected failures for deeper nonexistent paths, invalid share-name colon handling, and then creates `BAD\BAD\file` to test rename and hardlink behavior through `SMBmv`, setpathinfo, setfileinfo, and ntrename variants. Create-time comparisons prove whether operations addressed the intended object or just the share root.

`run_smb1_dfs_search_paths()` creates a file, captures a baseline directory listing for `SERVER\SHARE\*`, and verifies that equivalent DFS search patterns such as `\SERVER\SHARE\*`, `*`, `\*`, and `\SERVER\*` return the same names in the same order.

`run_smb1_dfs_operations()` executes a broad command matrix. For many SMB1 commands, short paths like `file` or `\BAD\file` are expected to resolve to the DFS root and therefore fail as directory operations or report root directory attributes, while full DFS-style paths like `\BAD\BAD\file` are expected to operate on the test file. It also captures known Windows-compatible oddities, such as `SMBctemp` returning `NT_STATUS_FILE_IS_A_DIRECTORY` for all tested DFS-share variants.

`run_smb1_dfs_check_badpath()` isolates the Bug 15419 regression by checking that `SMBcheckpath` on `\x//\/` succeeds.

## State And Persistence Behavior
The suite mutates the connected DFS share by creating and deleting temporary files, directories, renamed files, and hardlinks under paths such as `\BAD\BAD\file`, `\BAD\BAD\dir`, and command-specific names. Cleanup is best-effort and appears at the beginning and end of most tests. Many cleanup calls use delete-on-close through `smb1_dfs_delete()`, so leaked handles or early process termination can leave artifacts behind. No local persistent state is written, but the remote share contents and metadata are used as the test oracle.

## Dependencies And Integration Points
The file depends on Samba's SMB1 client internals (`smb1cli_ntcreatex`, `smb1cli_close`, raw `cli_smb`, `cli_smb_send`, `cli_trans`, `cli_trans_send`, request chaining, and byte-string marshalling helpers), talloc, tevent, NTSTATUS/WERROR utilities, time helpers, and generated protocol constants. It integrates with smbtorture via exported `run_*` functions and with the global torture connection settings (`host`, `share`, credentials, and related globals). It also uses Windows protocol behavior comments as compatibility expectations for Samba server behavior.

## Risks And Edge Cases
This test suite is sensitive to the exact server behavior of SMB1 DFS path normalization. Several expected statuses are intentionally surprising: short paths can map to the share root, invalid server-name characters can be ignored, only `:` is treated as invalid in a DFS share name, setpathinfo rename/link with separators returns `NT_STATUS_NOT_SUPPORTED`, handle-based setfileinfo rename/link returns `NT_STATUS_UNSUCCESSFUL`, and ctemp returns directory errors. These are compatibility constraints and are easy to break with cleanup refactors in path parsing.

The file contains hand-built SMB parameter/data blocks, UCS-2 conversion, manual info-level layouts, and manual directory-entry parsing. Risks include off-by-one string lengths, Unicode/null-termination differences, incorrect returned-handle extraction, and response parser assumptions. One suspicious detail is `smb1_nttrans_create()` reading the returned fnum from `param` rather than `rparam`; if intentional, it deserves a comment, and if not, it may reduce cleanup reliability. Tests also assume a writable, empty-enough DFS share and SMB1 availability, which many modern environments disable.

## Test Signals
The strongest signal is exact NTSTATUS compatibility for each raw SMB1 operation and exact object identity validation through create-time comparisons. Search tests add listing equivalence and parser validation for `SMB_FIND_FILE_BOTH_DIRECTORY_INFO`. Diagnostic output includes source line, operation, path, expected status, and actual status. Passing the suite indicates Samba's SMB1 DFS server path handling is aligned with the captured Windows-compatible behavior across open/create/delete/rename/link/search/attribute/checkpath/query operations.
