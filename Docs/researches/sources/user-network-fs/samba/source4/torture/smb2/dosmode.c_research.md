# sources/user-network-fs/samba/source4/torture/smb2/dosmode.c

## Purpose
`dosmode.c` contains two top-level SMB2 torture tests for DOS attribute behavior around hidden files. It verifies that explicit `FILE_ATTRIBUTE_HIDDEN`, Samba `hide files` behavior, and `hide dot files` behavior are visible through SMB2 metadata and directory enumeration. It also checks an overwrite edge case: overwriting a file that was made hidden explicitly must fail with an attribute mismatch, while overwriting files hidden by configured name rules should succeed.

## Important APIs, Types, And Functions
The file uses SMB2 connection, create, setinfo, getinfo, find, close, and deltree helpers. There are no local structs or suite initializer in this file; both functions are registered as simple top-level SMB2 tests by `smb2.c`.

Important functions are:

- `torture_smb2_dosmode()`: creates a test directory, creates `file`, explicitly sets its basic attributes to `FILE_ATTRIBUTE_HIDDEN`, validates the hidden bit by `RAW_FILEINFO_BASIC_INFORMATION`, checks that `NTCREATEX_DISP_OVERWRITE_IF` with normal attributes fails for that explicit hidden file, then creates and overwrites `hidefile` and `.dotfile` while expecting the hidden bit to be set by server configuration.
- `torture_smb2_async_dosmode()`: creates a hidden `file`, closes it, then uses `SMB2_FIND_BOTH_DIRECTORY_INFO` against the containing directory to verify the hidden bit appears in directory enumeration results. Despite the name, the code uses the normal `smb2_find_level()` wrapper rather than an explicit async request API.

Key request/response unions are `struct smb2_create`, `union smb_setfileinfo`, `union smb_fileinfo`, `struct smb2_find`, and `union smb_search_data`.

## Control Flow
Both tests establish their own SMB2 connection with `torture_smb2_connection()`, delete `torture_dosmode`, create it with `torture_smb2_testdir()`, and clean up in a shared `done:` path.

`torture_smb2_dosmode()` first creates `torture_dosmode\file` with normal attributes. It sends `RAW_SFILEINFO_BASIC_INFORMATION` by handle to set `FILE_ATTRIBUTE_HIDDEN`, then queries `RAW_FILEINFO_BASIC_INFORMATION` and asserts the bit is present. After closing, it attempts to reopen the same file with `NTCREATEX_DISP_OVERWRITE_IF` and normal attributes and expects `NT_STATUS_ACCESS_DENIED`. It then creates `torture_dosmode\hidefile`, expects the hidden bit to be present immediately, closes it, and verifies overwrite-if succeeds. The same create/query/overwrite sequence is repeated for `torture_dosmode\.dotfile`.

`torture_smb2_async_dosmode()` creates `file`, sets `FILE_ATTRIBUTE_HIDDEN`, closes the file handle, then issues a find request with pattern `file`, `SMB2_CONTINUE_FLAG_RESTART`, 0x1000 max response size, and `SMB2_FIND_BOTH_DIRECTORY_INFO`. It closes the directory handle before asserting the returned directory-info attributes include `FILE_ATTRIBUTE_HIDDEN`.

## State And Persistence Behavior
The remote state is the `torture_dosmode` directory and three files under it. Both tests delete the tree before and after execution. The tests intentionally persist a hidden attribute long enough to validate it by both handle-based query and directory enumeration.

The behavior under test depends on server-side persisted DOS attribute state and on configured name-based hiding rules. A file explicitly changed to hidden is expected to behave differently from files hidden by `hide files` or `hide dot files`: explicit hidden state causes the overwrite-if with normal attributes to fail, while rule-hidden files can be overwritten successfully.

Client-side state is minimal and stack-based. Handles are initialized to zeroed SMB2 handles and closed conditionally if still non-empty.

## Dependencies
The tests depend on Samba SMB2 client calls and torture assertions. Semantically, they depend on the target share being configured so that `hidefile` matches a `hide files` rule and `.dotfile` is hidden by `hide dot files`; otherwise the hidden-bit assertions for those names will fail. They also depend on DOS attribute storage/mapping in the server and VFS backend.

The file includes `system/time.h` but does not use time APIs directly. The actual integration comes through `torture/smb2/proto.h`, where these functions are declared and registered by the larger SMB2 suite.

## Integration Points
`smb2.c` registers these as `smb2.dosmode` and `smb2.async_dosmode`. They complement broader SMB2 create, setinfo, getinfo, and directory tests by focusing on the DOS mode rules that are often controlled by Samba share parameters rather than raw protocol fields alone.

These tests touch server code paths for create disposition handling, basic-info set/query, hidden attribute synthesis during create and find, and name-rule based DOS attribute evaluation. They are useful when changing VFS modules, DOS attribute backends, `hide files`, `hide dot files`, or SMB2 create overwrite checks.

## Risks
The tests are configuration-sensitive. If the test environment does not configure `hide files` to match `hidefile` and does not enable dotfile hiding, `torture_smb2_dosmode()` will fail even if generic SMB2 attribute handling works. The source comments assume those settings are present but the file itself does not skip when they are absent.

`torture_smb2_async_dosmode()` does not check `count` before dereferencing `d->both_directory_info`; it relies on `smb2_find_level()` returning at least one matching result for the created file. A server returning success with zero entries would cause invalid result handling. Cleanup calls `smb2_deltree(tree, dname)` even if connection setup partially failed, but the function returns early when connection setup fails.

The overwrite status expectation is specific: explicit hidden overwrite with normal attributes must return `NT_STATUS_ACCESS_DENIED`. Server behavior that returns a different attribute-mismatch status would be reported as a failure.

## Test Signals
Pass signals are successful basic-info set/query for `FILE_ATTRIBUTE_HIDDEN`, `NT_STATUS_ACCESS_DENIED` on overwrite-if of the explicitly hidden file, successful overwrite-if of `hidefile` and `.dotfile`, and a directory enumeration entry whose `both_directory_info.attrib` includes `FILE_ATTRIBUTE_HIDDEN`.

Useful failure signals distinguish attribute synthesis from overwrite policy: missing hidden bit on `hidefile` or `.dotfile` points to share configuration or name-rule mapping, while failure on explicit set/query points to DOS attribute persistence. A failure in `async_dosmode` but not `dosmode` points specifically to FIND result attribute propagation.
