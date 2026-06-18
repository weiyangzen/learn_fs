# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_notify.c

## Summary
Provides the common SMB1/SMB2 file change notification engine. It maintains per-open-directory notification buffers, records events even when no request is waiting, and implements a three-act async flow for long-lived notify requests.

## Main Responsibilities
- Validates notify requests against directory handles and `FILE_LIST_DIRECTORY`.
- Subscribes an ofile to node-level change events on first notify.
- Buffers `FILE_NOTIFY_INFORMATION` records per ofile.
- Parks notify requests without a worker thread and resumes them via taskq.
- Handles cancellation, close, delete-pending, subdirectory-change, and overflow events.
- Maps internal file actions to client completion filters.

## Key APIs
- `smb_notify_act1()`.
- `smb_notify_act2()`.
- `smb_notify_act3()`.
- `smb_notify_ofile()`.

## Important Behavior
`act1` validates parameters, subscribes the ofile if needed, and returns already buffered events immediately. If no events exist, it returns `NT_STATUS_PENDING`.

`act2` transitions the request from ACTIVE to WAITING_FCN1, clears `sr_worker`, installs `smb_notify_cancel()` as the cancel method, links the request into `nc_waiters`, and wakes it immediately if an event raced in.

`act3` runs after wakeup or cancel, restores the worker thread, removes the request from the waiter list, and consumes buffered events.

Notify buffers are destructive only when the last waiter consumes them. Multiple simultaneous waiters see the same pending events; the last waiter clears normal events while persistent close/delete indicators remain.

## Event Encoding
Normal actions append aligned `FILE_NOTIFY_INFORMATION` records to `nc_buffer`; the last entry's `NextEntryOffset` is patched to zero on consumption. Overflow, zero-length output, or too-small caller buffers result in `NT_STATUS_NOTIFY_ENUM_DIR`.

Internal actions such as delete pending and handle closed set event bits without appending response records.

## Dependencies
Used by SMB1 NT transact notify and SMB2 change notify finish paths. Relies on `smb_node_fcn_subscribe()`, taskq dispatch, request cancel states, mbuf-chain encoding/copying, and per-ofile mutex/list state.

## Risks
Recursive `WatchTree` support is represented as a subdirectory-change enum-dir signal, not true recursive monitoring. The source comments state recursive notify is optional and intentionally not implemented.

The notify buffer size is fixed on the first notify call for an ofile, matching Windows behavior but making later smaller buffers produce enum-dir fallback.
