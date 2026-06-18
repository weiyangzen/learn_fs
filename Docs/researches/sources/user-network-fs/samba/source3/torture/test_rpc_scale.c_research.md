# sources/user-network-fs/samba/source3/torture/test_rpc_scale.c

## Purpose
This file implements `run_rpc_scale`, an smbtorture load test for repeated asynchronous DCE/RPC pipe setup and basic spoolss RPC calls across multiple SMB connections. It repeatedly opens the `spoolss` named pipe, binds anonymously, calls `EnumPrinters`, closes the RPC client, and loops for `torture_numops` iterations per connection. The intent is to exercise connection scaling, named-pipe open/bind teardown behavior, RPC client lifetime management, and server stability under repeated RPC setup.

## Important APIs, Types, And Functions
`struct rpc_scale_one_state` holds one client's event context, `cli_state`, iteration count, active `rpc_pipe_client`, spoolss response buffer, and `EnumPrinters` result fields. `rpc_scale_one_send()` starts one per-client loop. Its callbacks are `rpc_scale_one_opened()`, `rpc_scale_one_bound()`, and `rpc_scale_one_listed()`. `rpc_scale_one_recv()` returns the final NTSTATUS.

`struct rpc_scale_state` aggregates all per-client requests. `rpc_scale_send()` starts one `rpc_scale_one_send()` per element in the talloc-sized `clis` array, and `rpc_scale_done()` completes once all have succeeded. `run_rpc_scale()` is the exported smbtorture entry point.

Important external APIs include `rpc_pipe_open_np_send/recv`, `rpccli_anon_bind_data()`, `rpc_pipe_bind_send/recv`, `dcerpc_spoolss_EnumPrinters_send/recv`, `smbXcli_conn_remote_name()`, `data_blob_talloc()`, and tevent request helpers.

## Control Flow
`run_rpc_scale()` allocates `torture_nprocs` client slots, opens each SMB connection, initializes a tevent context, and dispatches `rpc_scale_send()`. Each per-client request opens the spoolss named pipe, creates anonymous bind auth data, binds, builds a server string from the remote SMB name, allocates a 4096-byte response buffer, and calls `EnumPrinters` at level 1 with `PRINTER_ENUM_LOCAL`. On a successful WERROR result, it frees `state->rpccli`, decrements `num_iterations`, and either completes or starts another open/bind/list cycle. The aggregate request completes only when all clients finish their loops.

## State And Persistence Behavior
The test does not create durable server-side data. Its state is connection-oriented: SMB connections, RPC pipe handles, bind state, allocated response buffers, and returned printer metadata. Each iteration explicitly frees the RPC client, which triggers a synchronous close noted by the in-code comment. All local allocations are tied to the talloc stack frame or request states and are freed at function exit.

## Dependencies And Integration Points
This source depends on Samba RPC client infrastructure, generated spoolss client stubs, SMB named-pipe transport, tevent, and global torture parameters. It integrates with any server exposing the spoolss pipe over SMB named pipes. The test assumes anonymous binding to spoolss and a successful `EnumPrinters` call are acceptable in the target test environment.

## Risks And Edge Cases
The test is intentionally heavy: total pipe open/bind/list cycles are `torture_nprocs * torture_numops`. The synchronous close during `TALLOC_FREE(state->rpccli)` can serialize or block progress despite the async outer structure. `rpc_scale_one_bound()` constructs the server name with a trailing newline (`"\\%s\n"`), which is unusual and may be either intentional compatibility behavior or a typo-like quirk worth preserving until understood. A too-small 4096-byte buffer may cause non-OK spoolss WERRORs on servers with many printers if the call does not transparently handle `needed` sizing.

## Test Signals
Success requires every SMB connection to open, every named-pipe open and bind to succeed, every `EnumPrinters` RPC transport status to be OK, and every spoolss WERROR result to be OK. Failures are reported as NTSTATUS strings from `rpc_scale_send` or `rpc_scale_recv`, making this primarily a stability/load signal rather than a detailed functional printer enumeration test.
