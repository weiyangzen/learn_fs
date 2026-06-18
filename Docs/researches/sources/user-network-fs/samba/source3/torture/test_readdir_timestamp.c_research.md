# sources/user-network-fs/samba/source3/torture/test_readdir_timestamp.c

## Purpose
This file implements the `run_readdir_timestamp` smbtorture test. It stress-tests directory enumeration timestamp fidelity by creating many files through multiple SMB client connections, encoding each file's logical index into the low 16 bits of its last-write timestamp, and then verifying that `cli_list()` returns `file_info.mtime_ts` values matching the encoded filename index. The test is aimed at readdir/listing paths where timestamp metadata can be cached, rounded, reordered, or returned from a different metadata source than direct file operations.

## Important APIs, Types, And Functions
Key state types are `create_ts_state`, `create_ts_files_state`, `create_files_state`, and `list_cb_state`. The first three are tevent request state containers used to compose asynchronous file creation across one file, one client, and all clients respectively. `list_cb_state` accumulates the number of listed files and a boolean timestamp validation result.

The main async chain starts in `create_ts_send()`: it calls `cli_ntcreate_send()`, receives the handle in `create_ts_opened()`, adjusts the last-write time with `cli_setfileinfo_ext_send()`, waits 100 ms with `tevent_wakeup_send()`, writes a small payload with `cli_write_send()`, and marks the handle delete-on-close with `cli_nt_delete_on_close_send()`. `create_ts_recv()` returns the open file number so the test can keep handles alive until enumeration has completed.

`create_ts_files_send()` launches `num_files` `create_ts_send()` requests for one client. `create_files_send()` launches one `create_ts_files_send()` per SMB client. `list_cb()` parses the numeric suffix after the underscore in listed names with `smb_strtoull()` and compares it with the low 16 bits of `f->mtime_ts.tv_sec`.

## Control Flow
`run_readdir_timestamp()` opens `torture_nprocs` connections, creates or reuses the `readdir_ts` directory, initializes a tevent context, and dispatches `create_files_send()` for `torture_nprocs * torture_numops` files. The asynchronous fan-out means many creates and metadata updates are in flight concurrently. After `tevent_req_poll_ntstatus()` completes and `create_files_recv()` returns the handle arrays, the test enumerates `readdir_ts\*` through `cli_list()`. It then checks both the count and the timestamp match flag before freeing the client array, which also releases the open handles and triggers delete-on-close cleanup.

## State And Persistence Behavior
The test creates transient files named `readdir_ts/<client_index>_<file_index>`. It intentionally leaves file handles open during the listing phase and sets delete-on-close rather than deleting immediately. Persistent state is limited to the test directory and any files left behind if the process aborts before handle cleanup. Timestamp state is deliberately mutated: the test preserves most of the server-returned last-write time but overwrites the low 16 bits of `tv_sec` with the expected index.

## Dependencies And Integration Points
The file depends on Samba client and event infrastructure: `cli_ntcreate_send/recv`, `cli_setfileinfo_ext_send/recv`, `cli_write_send/recv`, `cli_nt_delete_on_close_send/recv`, `cli_list`, `samba_tevent_context_init`, `tevent_req_*`, and the global torture knobs `torture_nprocs` and `torture_numops`. It integrates with smbtorture through the exported `run_readdir_timestamp()` entry point and with the SMB server under test through normal SMB create, setinfo, write, delete-on-close, mkdir, and directory listing operations.

## Risks And Edge Cases
The test is timing-sensitive because it waits 100 ms between setting the timestamp and writing file data. That wait is meant to avoid accidental timestamp equality or server timestamp coalescing, but slow or coarse timestamp backends can still affect results. `create_ts_written()` calls `tevent_req_nterror(subreq, status)` instead of reporting on the parent `req`, which looks suspicious because failures could be recorded on the just-freed subrequest path rather than the outer request. The filename parser ignores entries without an underscore or numeric suffix, so unexpected files in `readdir_ts` can affect the found count only when they look like test files. Runs against shares with preexisting matching files or failed prior cleanup may produce count mismatches.

## Test Signals
Success requires all async create/setinfo/write/delete-on-close operations to complete, `cli_list()` to return OK, `state.found` to equal `torture_nprocs * torture_numops`, and every listed test file to have low timestamp bits matching its filename suffix. Diagnostic output names failed SMB operations, expected and actual counts, and timestamp mismatches.
