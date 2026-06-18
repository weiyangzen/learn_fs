# sources/user-network-fs/samba/source4/torture/rpc/bench.c

## Purpose
`bench.c` is a simple RPC benchmark for SRVSVC share enumeration. It repeatedly calls `NetShareEnumAll` at several information levels for a configured time and reports queries per second.

## Important APIs, types, and functions
The exported entry point is `torture_bench_rpc()`. Helpers are `test_NetShareEnumAll()` and `bench_NetShareEnumAll()`. It uses `dcerpc_srvsvc_NetShareEnumAll_r()`, `struct srvsvc_NetShareEnumAll`, `struct srvsvc_NetShareInfoCtr`, share container types for levels 0, 1, 2, 501, and 502, `ndr_table_srvsvc`, and `timeval_elapsed()`.

## Control flow
`torture_bench_rpc()` opens a SRVSVC RPC pipe and calls the benchmark helper. The benchmark reads the `timelimit` setting, then loops until elapsed time exceeds that limit. Each iteration creates a temporary talloc context, calls `test_NetShareEnumAll()`, frees the context, increments a count, and optionally prints progress every 50 iterations. `test_NetShareEnumAll()` builds a server UNC from the RPC server name and calls `NetShareEnumAll` for levels 0, 1, 2, 501, and 502, resetting the resume handle and union arm for each level.

## State and persistence behavior
No server data is changed. Client state is the open SRVSVC pipe, per-iteration temporary allocations, resume handle values, and benchmark counters. Server state observed is the share list.

## Dependencies and integration points
The benchmark depends on SRVSVC generated stubs, DCE/RPC connection setup, talloc, and torture settings `timelimit` and `progress`. It exercises share-enumeration marshalling, server share database access, and RPC throughput.

## Risks and edge cases
The helper sets `ret = false` only for transport failures; WERROR failures print and continue without changing `ret`, so benchmark success can mask per-level operation failures. Share level 502 may require privileges or return access errors on some servers. The denominator uses elapsed wall time and can be noisy for very short timelimits.

## Test signals
Useful signals are successful SRVSVC bind, no transport failures for all tested levels, stable progress output, and final queries-per-second numbers. For correctness, logs should be checked for per-level WERROR failures even if the benchmark returns true.
