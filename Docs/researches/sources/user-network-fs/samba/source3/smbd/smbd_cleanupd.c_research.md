# sources/user-network-fs/samba/source3/smbd/smbd_cleanupd.c

## Purpose
Implements the smbd cleanup daemon request. It listens for shutdown and cleanup notifications, drains child cleanup records, removes stale child entries, cleans profiling and messaging resources, and completes its tevent request on shutdown.

## Important APIs, Types, and Functions
`smbd_cleanupd_send()` creates state and registers handlers for `MSG_SHUTDOWN` and `MSG_SMB_NOTIFY_CLEANUP`. `smbd_cleanupd_shutdown()` completes the request. `smbd_cleanupd_process_exited()` traverses `cleanupdb`, collects child PID records, then performs cleanup outside the traverse. `smbd_cleanupd_recv()` follows the standard tevent recv pattern.

## Control Flow
The send function returns an in-progress tevent request after message registration. On cleanup notification, the handler traverses `cleanupdb` read-only into a temporary linked list, avoiding writer interactions while locked. It then deletes each child record, calls `smbprofile_cleanup(child_pid, parent_pid)`, runs `messaging_cleanup()`, tolerates `ENOENT`, logs, and frees the frame.

## State and Persistence
Persistent input is `cleanupdb`, which records child PIDs and an `unclean` flag. Runtime state stores only the parent PID. Cleanup removes records and messaging/profile leftovers associated with dead children.

## Dependencies and Integration Points
Depends on Samba messaging, tevent NTSTATUS helpers, `cleanupdb`, server ID/process utilities, smbd profiling cleanup, and locking prototypes. It is triggered by parent/child smbd process management when workers exit.

## Risks
Cleanup runs asynchronously in response to messages; missed notifications can leave records until the next notification. Failure to delete cleanupdb records is logged but does not stop other child cleanup. The `unclean` flag is collected but not used here, so any differentiated cleanup policy must live elsewhere or be added carefully.

## Test Signals
Test message registration failures, shutdown completion, cleanup of multiple child records, cleanupdb traverse failure, deletion failure logging, idempotent behavior when messaging cleanup returns `ENOENT`, and profile cleanup with the expected parent PID.
