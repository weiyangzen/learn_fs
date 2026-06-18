
# sources/user-network-fs/samba/source4/torture/nbt/query.c

## Purpose
`query.c` implements the `nbt.bench.namequery` benchmark. It measures how many asynchronous NetBIOS name queries a server can answer within a configured time limit while keeping a bounded number of outstanding requests.

## Important APIs, Types, And Functions
`struct result_struct` tracks `num_pass` and `num_fail`. `increment_handler()` is the asynchronous completion callback for `struct nbt_name_request`; it increments pass/fail depending on `req->state` and frees the request. `bench_namequery()` sets up the query template, sends asynchronous `nbt_name_query_send()` requests, runs the event loop, drains outstanding requests, and reports queries per second. `torture_bench_nbt()` registers the `bench` suite with the `namequery` simple test.

## Control Flow
`bench_namequery()` obtains an NBT socket with `torture_init_nbt_socket()`, resolves the target through `torture_nbt_get_name()`, initializes a `struct nbt_name_query` with retries disabled, one-second timeout, direct unicast destination, and non-WINS lookup mode. For the configured `timelimit` it maintains fewer than ten outstanding requests, attaches `increment_handler()` to each request, and advances tevent once per outer loop. After time expires it continues processing events until every sent request has either passed or failed, then reports throughput.

## State And Persistence
All benchmark state is in memory under the torture context. There is no remote persistent state because the test only queries names. The only long-lived observable state is benchmark output showing pass rate and failures.

## Dependencies
The file depends on NBT socket/query APIs, tevent, resolver/loadparm helpers from `nbt.c`, torture settings, timeval helpers, and the target server's NetBIOS name service. It uses `lpcfg_nbt_port()` for the destination port.

## Integration Points
The suite is registered by `torture_nbt_init()` through `torture_bench_nbt()`. It shares target resolution and socket creation with the rest of the NBT torture area. The `progress` torture setting controls periodic output.

## Risks
The benchmark divides by elapsed time and pass count, so very short time limits or no replies can produce unhelpful throughput output. The completion callback treats any non-`NBT_REQUEST_DONE` state as failure without distinguishing timeout, network error, or protocol error. With retries set to zero and only ten in-flight requests, results are intentionally latency-sensitive and may underrepresent high-throughput servers on lossy networks.

## Test Signals
Signals are the final queries-per-second line, failure count, periodic progress every thousand sends, and successful draining of all outstanding requests. Useful regression signals include stable pass/fail accounting and absence of request leaks under timeout-heavy conditions.
