# sources/user-network-fs/samba/source4/torture/smb2/credits.c

## Purpose

`credits.c` implements the SMB2 crediting torture suite. It validates credit grants during session setup and ordinary requests, MID-window recovery after a skipped message ID, and the server's max-async-credit enforcement for IPC named-pipe reads and change-notify requests across one connection, two connections, and SMB3 multichannel.

## Important APIs, Types, and Functions

- Credit and transport APIs: `smb2cli_conn_get_cur_credits`, `smb2cli_conn_set_max_credits`, `smb2cli_conn_get_mid`, `smb2cli_conn_set_mid`, `smb2_transport_credits_ask_num`, and `smbXcli_conn_disconnect`.
- Connection/session APIs: `torture_smb2_connection_ext`, `smb2_connect`, `smb2_session_channel`, `smb2_session_setup_spnego`, `smb2_tree_channel`, `smb2_logoff`, and `torture_smb2_tree_connect` patterns through the torture harness.
- Async request APIs: `smb2cli_read_send`, `smb2cli_read_recv`, `smb2cli_read_set_notify_async`, `smb2cli_notify_send`, `smb2cli_notify_recv`, `smb2cli_notify_set_notify_async`, `tevent_create_immediate`, `tevent_schedule_immediate`, `tevent_wakeup_send`, `tevent_req_cancel`, and `tevent_req_poll`.
- IPC setup calls: low-level `smb2cli_create` for `NDR_LSARPC_NAME`, `smb2cli_ioctl` with `FSCTL_NAMED_PIPE_READ_WRITE`, and a static DCERPC LSA bind byte sequence.
- Main state carriers are `test_ipc_async_credits_state`, `test_ipc_async_credits_loop`, `test_notify_async_credit_state`, and `test_notify_async_credit_loop`.

## Control Flow

The suite begins with direct credit grant tests. `test_session_setup_credits_granted()` logs off the initial session, reconnects with `options.max_credits = 65535`, and requires at least 8192 granted credits. `test_single_req_credits_granted()` reconnects with one credit, raises the client-side max to 65535, sends a create, and requires the server to grant at least 8192 credits. `test_crediting_skipped_mid()` reconnects with 8192 credits, deliberately skips a MID, sends many writes without advancing the client credit window, then reuses the skipped MID on close and verifies the full 8192-credit window is restored.

IPC max-async-credit tests are driven by `test_ipc_max_async_credits()`. It verifies each tree starts with `num_loops` credits, opens `num_loops` LSA named-pipe handles per tree, sends a DCERPC bind ioctl on each handle, then schedules async pipe reads. Completion callbacks count `NT_STATUS_PENDING`, `NT_STATUS_INSUFFICIENT_RESOURCES`, and cancellation results. The expected steady state is `max_async_credits - 1` pending operations and the remaining over-limit operations rejected with insufficient resources. Wrappers create one IPC connection, two IPC connections, multichannel IPC, and a zero-length max-data variant.

Notify max-async-credit tests mirror the IPC shape through `test_notify_max_async_credits()`. The wrappers create or reuse `TESTDIR`, ask for `max_async_credits + 2` credits, open directory handles, issue async notify requests, verify the same pending/insufficient-resource split, close handles to cancel pending notifies, and check that pending requests end with `NT_STATUS_NOTIFY_CLEANUP`.

## State and Persistence Behavior

The tests mutate transport credit configuration and sometimes intentionally disconnect the original connection at the end. They create temporary files such as `single_req_credits_granted.dat` and `skipped_mid.dat`, and a temporary directory `test_max_async_credits` for notify tests. IPC tests open named-pipe handles and leave them scoped to per-test state allocations; cleanup frees state, closes/cancels requests, unlinks temporary files, removes `TESTDIR`, and disconnects transports.

The async state objects persist counters across callbacks: started operations, received statuses, pending statuses, insufficient-resource statuses, stop flags, request pointers, FIDs, and per-loop status. These counters are the authoritative test state for deciding whether the server enforces the async-credit limit.

## Dependencies and Integration Points

This file depends on the SMB2 client stack, SMBXCLI base credit accounting, tevent, command-line credentials, resolver and loadparm context, NDR LSA constants, and the torture SMB2 harness. It integrates as `torture_smb2_crediting_init()` with one-tree and two-tree tests. Runtime settings include `host`, `share`, `maxasynccredits`, and `samba4`; the two-connection and IPC multichannel tests skip against Samba4 source4 RPC server due to open-file pressure.

The tests are integration-heavy: they exercise server-side credit grant policy, MID window accounting, async pending limits, named-pipe RPC behavior, notify cancellation, and multichannel session binding.

## Risks and Edge Cases

- Expected values assume a default max async credits of 512 unless overridden; mismatched server configuration should use `maxasynccredits`.
- Tests intentionally stress many pending handles and requests, so resource limits, timeouts, and source4 RPC server file descriptor pressure can produce environmental failures.
- MID manipulation bypasses normal client-side sequencing and can disconnect nonconforming servers; cleanup resets the MID to avoid client-side confusion.
- The async loops use a 10-second wakeup and require tevent progress; slow systems may fail due to timing rather than semantic credit bugs.
- Multichannel tests require server and client support for channel binding and SPNEGO setup.

## Test Signals

Pass signals are exact credit counts after reconnect or request crediting, successful recovery after skipped MID reuse, exact pending and insufficient-resource counts for IPC reads and notify operations, correct cancellation statuses (`NT_STATUS_CANCELLED` for pipe reads and `NT_STATUS_NOTIFY_CLEANUP` for notify), successful cleanup closes, and no unexpected async stop flags.
