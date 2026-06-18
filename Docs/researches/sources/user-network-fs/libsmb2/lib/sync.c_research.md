<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/sync.c -->
# sources/user-network-fs/libsmb2/lib/sync.c

Purpose: Provides the synchronous public libsmb2 API by blocking on the asynchronous PDU API and servicing the SMB socket until callbacks complete.

Important APIs, types, and functions: Central helper `wait_for_reply` polls `smb2_get_fd` with `smb2_which_events`, calls `smb2_timeout_pdus` and `smb2_service`, and observes `sync_cb_data`. Synchronous wrappers include share connect/disconnect, open/close, directory open, read/write/pread/pwrite, mkdir/rmdir/unlink, stat/fstat/statvfs, rename, truncate/ftruncate, readlink, echo, notify_change, and share_enum.

Control flow: Each wrapper allocates or reuses a `sync_cb_data`, starts the matching async operation, waits, maps callback status/pointer to the synchronous return value, then frees the callback data or transfers ownership to the returned object where required. Callback variants handle shutdown/cancelled cases and command-data pointers.

State and persistence behavior: State is transient per call, except `smb2->connect_cb_data` is reused for connect/disconnect. Some async PDUs own and free callback data through destructor arguments. Returned handles, directories, notify results, and share enum replies outlive the sync call and must be freed by caller-specific APIs.

Dependencies and integration points: Depends on libsmb2 raw async APIs, poll, timeout handling, private socket fields, and callback conventions. Utilities such as `smb2-cp` and `smb2-ls` rely on these wrappers.

Risks: Several wait-failure branches set `SMB2_STATUS_CANCELLED` and return without freeing local callback data, relying on later async cancellation behavior; this is subtle and leak-prone if cancellation does not occur. `smb2_echo` returns `-ENOMEM` for not connected. Blocking calls cannot be composed inside an external event loop without tying up the caller thread.

Test signals: Covered by shell tests for ls, mkdir, cp, cat, socket-error injection, valgrind, and cancellation paths in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/sync.c -->
