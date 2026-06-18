# sources/user-network-fs/samba/source3/smbd/notifyd/fcn_wait.c

## Purpose
`fcn_wait.c` is a small asynchronous helper used by tests and tooling to register one file-change-notify interest with notifyd and wait for matching `MSG_PVFS_NOTIFY` events. It wraps notifyd's messaging protocol in a tevent request interface.

## Important APIs, Types, and Functions
The public functions are `fcn_wait_send()` and `fcn_wait_recv()`. `struct fcn_wait_state` holds the tevent context, messaging context, notifyd server id, watched path, active filtered-read subrequest, and a queue of received `struct fcn_event` records. `fcn_wait_filter()` validates incoming messages and queues matching events. `fcn_wait_cancel()` sends a delete-style `MSG_SMB_NOTIFY_REC_CHANGE` and completes the request with `NT_STATUS_CANCELLED`.

## Control Flow
`fcn_wait_send()` creates a tevent request, starts `messaging_filtered_read_send()` with `fcn_wait_filter()`, sends a registration record to notifyd, and installs cleanup and cancel hooks. The helper uses the address of its state object as `notify_instance.private_data`. When a message arrives, `fcn_wait_filter()` accepts only `MSG_PVFS_NOTIFY`, validates payload size and nul termination, copies the fixed part out to avoid alignment issues, compares `msg.private_data` with the state pointer, duplicates the complete message into the event queue, and notifies the parent request without consuming the filtered read. `fcn_wait_recv()` pops queued events and returns `NT_STATUS_RETRY` when no event is ready.

## State and Persistence
State is per tevent request and disappears with its talloc tree. Events are stored as a linked list under the state. No persistent database is written by this helper; notifyd persists interest in its in-memory db until cancellation or process cleanup. Cleanup frees the filtered-read subrequest, and cancellation explicitly unregisters from notifyd.

## Dependencies and Integration Points
This code depends on `notifyd.h` message formats, Samba messaging filtered reads, tevent request helpers, and NTSTATUS mapping. It integrates with `test_notifyd.c`, which uses it to validate trigger delivery and registration deletion.

## Risks and Edge Cases
Using an in-process pointer as cross-message private data is suitable for local tests but is not a stable external identifier. If cancellation's delete message fails, the helper returns false and may leave notifyd state behind. `fcn_wait_recv()` does not free the popped event explicitly after `DLIST_REMOVE`, so event lifetime follows the request context. Events are appended in arrival order; a TODO notes that timestamp sorting is not implemented.

## Test Signals
`test_notifyd_trigger1` verifies that a registered wait receives a matching trigger. `test_notifyd_dbtest1` verifies that `fcn_wait_send()` adds the caller to notifyd's database and that `tevent_req_cancel()` removes it. Additional useful tests would cover non-matching private data, malformed notify payloads, multiple queued events, and failed unregister.
