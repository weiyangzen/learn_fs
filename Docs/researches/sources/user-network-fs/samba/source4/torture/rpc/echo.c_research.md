# sources/user-network-fs/samba/source4/torture/rpc/echo.c

## Purpose
`echo.c` is the Samba torture suite for the test `rpcecho` interface. It validates basic scalar calls, conformant arrays, large source/sink data, strings, unions, enums, pointer depth, asynchronous multiplexed calls, and disabled timeout behavior.

## Important APIs, types, and functions
The file registers against `ndr_table_rpcecho`. Test functions include `test_addone`, `test_echodata`, `test_sourcedata`, `test_sinkdata`, `test_testcall`, `test_testcall2`, `test_sleep`, `test_enum`, `test_surrounding`, and `test_doublepointer`. `TEST_ADDONE` is a macro for repeated scalar assertions. `test_sleep` uses `dcerpc_echo_TestSleep_r_send`, `tevent_req_set_callback`, `tevent_loop_once`, and `dcerpc_echo_TestSleep_r_recv` to validate concurrent async behavior. A timeout test exists under `#if 0`.

## Control flow
`torture_rpc_echo()` creates the suite, adds one RPC tcase, and registers all enabled tests. Scalar and data tests build a request, call the generated stub, and compare returned values or byte patterns. `test_sleep` skips in quick mode; otherwise it opens a second echo connection using the same transport and association group with `DCERPC_CONCURRENT_MULTIPLEX`, sends three sleep calls with decreasing durations, and verifies completions arrive asynchronously and not serially. The disabled timeout code documents intended timeout/destruction behavior but is not compiled.

## State and persistence behavior
The suite has no persistent server-side state. It allocates temporary buffers and a second pipe for async testing. Large source/sink tests intentionally move hundreds of kilobytes unless quick mode plus validation flags reduce the sizes. Random lengths and scalar values make runs non-identical but still deterministic in expected byte patterns.

## Dependencies and integration points
It depends on generated echo NDR client stubs, Samba torture RPC helpers, talloc, tevent, binding flag inspection, and transport-aware connection helpers. The suite is a broad integration signal for NDR marshalling, DCE/RPC binding behavior, event-loop progress, and concurrent multiplexing support.

## Risks and edge cases
Large data tests can be slow under validation flags or constrained transports, which is why quick mode reduces sizes. Async timing uses rounded wall-clock differences and can be sensitive to busy servers; it tolerates one-second overhead but fails if sleeps appear serialized. The timeout test is disabled because it needs repair for `ncacn_np`, preserving a known coverage gap.

## Test signals
Signals include exact add-one arithmetic including wraparound cases, byte-for-byte echo/source data validation, string round-trip equality, `TestCall2` NTSTATUS results for levels 1 through 7, enum/pointer/conformant-array success, and async sleep completion timing. Quick-mode skips are explicit for long-running sleep coverage.
