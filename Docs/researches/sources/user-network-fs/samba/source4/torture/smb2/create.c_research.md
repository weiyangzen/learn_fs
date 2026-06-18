# sources/user-network-fs/samba/source4/torture/smb2/create.c

## Purpose

`create.c` is a large SMB2 torture-suite source file that validates SMB2 CREATE/open semantics, create-context blobs, security descriptor handling, directory creation races, time-warp snapshot behavior, file-id stability, quota fake file metadata, path length limits, and no-stream behavior. It registers four suites: `create`, `twrp`, `fileid`, and `create_no_streams`.

## Important APIs, Types, and Functions

- Core SMB2 calls: `smb2_create`, `smb2_create_send`, `smb2_create_recv`, `smb2_getinfo_file`, `smb2_setinfo_file`, `smb2_read`, `smb2_find_level`, `smb2_lock`, `smb2_util_write`, `smb2_util_close`, `smb2_util_unlink`, `smb2_deltree`, `smb2_util_mkdir`, and `smb2_util_rmdir`.
- Low-level async client calls: `smb2cli_create_send`, `smb2cli_create_recv`, `tevent_req_set_callback`, `tevent_req_poll`, and `tevent_loop_once`.
- Security APIs: `security_descriptor_dacl_create`, `security_descriptor_dacl_add`, `security_descriptor_copy`, `security_ace_create`, `security_descriptor_dacl_insert`, `dom_sid_parse_talloc`, and `dom_sid_string`.
- Test assertion and reporting helpers: `torture_assert_*`, `torture_fail_goto`, `torture_result`, `torture_comment`, and local macros such as `CHECK_STATUS`, `CHECK_EQUAL`, `CHECK_NTTIME`, `CHECK_ALL_INFO`, `SET_ATTRIB`, and `CHECK_ACCESS_FLAGS`.
- Important state structs include `struct smb2_create`, `union smb_open`, `union smb_fileinfo`, `union smb_setfileinfo`, `struct smb2_handle`, and the async directory-visibility structs `test_mkdir_visible_state` and `test_mkdir_visible_open`.

## Control Flow

The file is organized as independent static test functions that each construct SMB2 request structs, perform operations against a test share, verify returned status and metadata, then clean up paths and handles. `torture_smb2_create_init()` registers the main create tests, `torture_smb2_twrp_init()` registers snapshot/time-warp tests, `torture_smb2_fileid_init()` registers file-id tests, and `torture_smb2_create_no_streams_init()` registers invalid stream-name tests for shares without streams support.

The create tests begin with protocol edge cases in `test_create_gentest()` and `test_create_blob()`: invalid create options, invalid attributes, desired-access bit masks, stream creates, maximal-access output, allocation size, durable open, timewarp context, query-on-disk-id context, and create-blob tag length handling. `test_smb2_open()` then walks create disposition behavior, validates create response timestamps/sizes/attributes against getinfo, and repeats the checks for directories.

Concurrency and race coverage is implemented with multi-connection tests. `test_smb2_open_multi()` fires concurrent create requests for the same filename and expects exactly one success plus name collisions. `test_mkdir_dup()` performs the same style of race for directory `OPEN_IF`, expecting one `CREATED` and one `EXISTED`. `test_mkdir_visible()` uses 50 async low-level create loops that repeatedly try to create files inside a directory before the directory create completes; after the directory appears with inherited deny ACEs, each loop must resolve to `NT_STATUS_ACCESS_DENIED` rather than a stale path-not-found or unauthorized success.

The TWRP suite parses `twrp_snapshot` in `@GMT-YYYY.MM.DD-HH.MM.SS` form, converts it to an NT time, and sends SMB2 create requests with `io.in.timewarp`. It verifies read-only snapshot behavior: opens of existing objects succeed, attempts to write, delete, truncate, rename, hardlink, change ACLs, or create new files/directories fail with write-protection or cross-device status. It also validates stream reads, root opens, and directory-listing file IDs under a snapshot.

The file-id suite uses `query_on_disk_id` and `RAW_FILEINFO_SMB2_ALL_INFORMATION` to ensure file IDs are stable across create/open/overwrite, base file writes, stream creates/opens/overwrites, metadata setinfo operations, directory stream operations, and directory listings. `test_fileid_unique_object()` creates 100 files or directories and checks all returned IDs are unique with a brute-force pairwise comparison.

## State and Persistence Behavior

Tests persist only temporary share objects such as `test_create.dat`, `smb2_open`, `mkdir_dup`, `mkdir_visible`, and file-id test trees. The normal pattern is cleanup before and after each test with `smb2_deltree`, `smb2_util_unlink`, or `smb2_util_rmdir`. Handles are closed explicitly, often guarded with `smb2_util_handle_empty`.

Security descriptor tests persist ACL changes long enough to verify inheritance and access behavior. `test_create_acl_ext()` creates files and directories with initial DACLs and attributes, then verifies them with helper APIs. `test_create_null_dacl()` deliberately mutates a file between inherited DACL, NULL DACL, zero-ACE DACL, and empty descriptor states, validating the resulting access rules before cleanup and disconnect/logoff. `test_mkdir_visible()` persists a deny ACE on a base directory to exercise visibility and inherited denial under concurrent requests.

TWRP tests are stateful against pre-existing snapshot fixtures supplied through torture settings (`twrp_file`, `twrp_stream`, `twrp_snapshot`, `twrp_stream_size`). They do not create the snapshot data; they verify server behavior when historical views are opened with the timewarp create context.

## Dependencies and Integration Points

The source depends on Samba's SMB2 client library, torture harness, tevent event loop, security descriptor/NDR types, command-line credentials, and filesystem/system helpers. It integrates into the SMB2 torture test registry through exported suite initializers, which are discovered by the wider torture framework. Several tests depend on runtime settings: `samba4`, `hide_on_access_denied`, `interactive`, `twrp_*`, and the target platform checks such as `TARGET_IS_WIN7`.

The tests assert Windows-compatible semantics in many places. The expected masks in `test_create_gentest()`, the stream/base-file file-id expectations, the snapshot write-protection statuses, and the quota fake-file timestamps/attributes are all integration signals for server compatibility and regressions in create processing, VFS allocation reporting, stream support, ACL mapping, durable/timewarp create contexts, and file-id derivation.

## Risks and Edge Cases

- Several expected masks and status codes are exact and platform-sensitive; server behavior changes may require conditional expectations rather than blanket updates.
- Async race tests depend on event-loop progress and timing; failures can indicate real races but may also expose transport timeouts or overloaded test hosts.
- Cleanup is broad (`smb2_deltree`) and uses fixed names, so parallel execution against the same share namespace can interfere.
- `test_path_length_test()` is interactive-only because it probes path limits destructively and can leave deep directory trees if interrupted.
- TWRP tests depend on correctly provisioned snapshot fixtures and GMT parsing; missing settings intentionally skip or fail.
- Security descriptor tests rely on the server accepting owner/DACL updates and on share configuration such as `hide_on_access_denied`.

## Test Signals

Strong pass signals include exact NT status matches for create dispositions and invalid inputs, response metadata matching `RAW_FILEINFO_*` queries, successful ACL/attribute verification, correct race outcome counts, expected snapshot write-protection failures, stable file IDs across streams and metadata changes, unique IDs for 100 created objects, quota fake-file zero timestamps and hidden/system/directory/archive attributes, and `NT_STATUS_OBJECT_NAME_INVALID` on stream names when streams are disabled.
