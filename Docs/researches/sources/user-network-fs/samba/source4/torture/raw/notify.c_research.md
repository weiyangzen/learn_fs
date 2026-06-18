# sources/user-network-fs/samba/source4/torture/raw/notify.c

## Purpose
`notify.c` defines the raw SMB change-notify torture suite. It validates directory change notification delivery, buffering, cancellation, recursive watching, completion-filter masks, teardown behavior, secondary tree-connect behavior, overflow semantics, base-directory exclusion, and reply alignment.

## Important APIs, Types, and Functions
- Central raw API is `smb_raw_changenotify_send()`/`smb_raw_changenotify_recv()` using `union smb_notify` at `RAW_NOTIFY_NTTRANS`.
- Directory handles are opened with raw `NTCREATEX` directory options.
- `CHECK_WSTR` validates Unicode names and wire flags.
- `check_rename_reply()` tolerates non-deterministic ordering among rename-related add/remove/modify events.
- `secondary_tcon()` creates another tree connect on the same session with `RAW_TCON_TCONX`.
- `timeout_cb()` is used by the alignment test to bound a pending notify receive.
- `torture_raw_notify()` registers tests `tcon`, `dir`, `mask`, `recursive`, `mask_change`, `file`, `tdis`, `exit`, `ulogoff`, `tcp_dis`, `double`, `tree`, `overflow`, `basedir`, and `alignment`.

## Control Flow
Most subtests create a dedicated `\\test_notify_*` directory, open a directory handle, arm a notify request, perform filesystem operations through one or two SMB clients, receive the notify reply, and assert count, action, and name. `test_notify_dir()` covers cancellation, mkdir/rmdir, buffered creates/unlinks, wildcard unlink propagation, per-handle buffers, and close-triggered zero-change replies. `test_notify_recursive()` compares recursive and non-recursive buffers across nested mkdir/create/rename/delete operations. `test_notify_mask()` iterates every completion-filter bit for operations such as create, unlink, rename, attribute/time change, write, and truncate.

Teardown tests arm a notify then issue `tdis`, `SMBexit`, `ulogoff`, or forced TCP disconnect and assert the resulting completion status. `test_notify_tree()` opens many watched directories at different depths, generates create/delete events, polls until each watcher sees its expected count, and validates recursive filtering. `test_notify_alignment()` creates names of lengths one through four and relies on the receive parser to validate four-byte alignment of multiple `CHANGE_NOTIFY_INFO` records.

## State and Persistence Behavior
Server-side state is a set of temporary test directories and files. Notify buffers are deliberately primed by sending and canceling requests before generating events. The suite uses multiple clients or tree connects to test cross-connection delivery and clustered server propagation. Cleanup exits sessions and deletes each dedicated base directory.

## Dependencies and Integration Points
The suite integrates with the Samba torture framework through `torture_raw_notify()`, using one-SMB or two-SMB test registration depending on whether cross-client operations are required. It depends on raw SMB notify marshalling, string wire validation, event-loop timers for timeout protection, and standard SMB filesystem helpers.

## Risks and Edge Cases
- Notify ordering can vary, so rename checks intentionally accept action/name triples in a small window.
- Several tests use sleeps or propagation polling; clustered, cloud, or slow filesystems can be flaky.
- Exact notify mask expectations vary by server family; the code already skips one Samba3 create-time case.
- Overflow behavior expects an OK reply with zero changes when the server-side buffer exceeds response capacity.
- Close, disconnect, and TCP failure paths are sensitive to request lifetime and transport error propagation.

## Test Signals
Signals include exact NT statuses (`OK`, `CANCELLED`, `INVALID_PARAMETER`, `LOCAL_DISCONNECT`), expected notification counts, action constants such as `NOTIFY_ACTION_ADDED` and `NOTIFY_ACTION_REMOVED`, Unicode name checks, depth-specific event totals, duplicate/unexpected name detection in alignment tests, and timeout failure if delayed notify replies do not arrive.
