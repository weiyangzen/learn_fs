# sources/user-network-fs/samba/source3/torture/test_async_echo.c

## Purpose
`test_async_echo.c` stresses concurrent asynchronous SMB and DCERPC operations on one connection. It issues a long RPC echo sleep, SMB echo requests, and intentionally failing large writes, then verifies the event loop drains all callbacks.

## Important APIs, types, and functions
`run_async_echo()` is the exported test. Callback helpers `rpccli_sleep_done`, `cli_echo_done`, and `write_andx_done` receive request statuses and decrement a shared outstanding counter. The test uses `cli_rpc_pipe_open_noauth`, generated `dcerpc_echo_TestSleep_send/recv`, `cli_echo_send/recv`, and `cli_write_andx_send/recv`.

## Control flow
The test opens a torture SMB connection, opens the rpcecho pipe, starts a 15-second RPC sleep, starts one SMB echo, then loops ten times issuing a `cli_write_andx` to fnum `4711` and another echo. It runs `tevent_loop_once` until all callbacks have decremented `num_reqs` to zero.

## State and persistence behavior
State is transient: one event context, one SMB connection, one RPC pipe, outstanding request count, and a zeroed 64 KiB buffer. The invalid write handle should not persist data.

## Dependencies and integration points
It depends on the rpcecho RPC interface being available on the server and on Samba async client APIs. It is registered in the source3 torture harness.

## Risks and test signals
The test is mainly a concurrency and request-multiplexing signal. Deadlocks, missed callbacks, or event-loop failures indicate async client regressions. Some callback statuses may be expected failures for invalid writes, so the key signal is completion rather than every operation succeeding.
