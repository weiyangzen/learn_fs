
# sources/user-network-fs/samba/source4/torture/nbt/winsbench.c

## Purpose
`winsbench.c` implements the `nbt.bench-wins.wins` benchmark. It measures WINS server throughput under a random mixture of name registrations, releases, and queries across a configurable pool of generated names.

## Important APIs, Types, And Functions
`struct wins_state` stores benchmark configuration and counters: number of names, per-name registered flags, pass/fail counts, server/port, local IP, and TTL. `struct idx_state` associates an async request with a name index. `generate_name()` creates deterministic names like `WINSBench%6u` with type `0x4`. `register_handler()`, `release_handler()`, and `query_handler()` receive async completions, update pass/fail counts, and maintain `registered[idx]`. `generate_register()`, `generate_release()`, and `generate_query()` construct and send one async NBT request. `generate_request()` chooses a register roughly one-fifth of the time, release roughly one-twentieth of the remaining calls, otherwise query. `bench_wins()` runs the timed benchmark and reports throughput. `torture_bench_wins()` registers the `bench-wins` suite.

## Control Flow
`bench_wins()` resolves the WINS target with `torture_nbt_get_name()`, allocates `wins_state`, sizes the name pool from global `torture_entries`, selects a local interface IP, binds the NBT socket, and runs until `timelimit` seconds elapse. The loop maintains fewer than ten outstanding requests, sends a generated request for `num_sent % num_names`, periodically reports progress, and advances the tevent loop. After time expires it drains outstanding requests, prints final operations per second and failures, frees the socket, and returns.

## State And Persistence
In-memory state tracks whether each generated name is believed registered. Remote WINS state is intentionally mutated: registrations add names and releases remove them. TTL is set to the benchmark time limit, limiting but not eliminating residue if the benchmark exits early or releases fail. Registered state is probabilistic from the client's viewpoint because query failures against names believed registered are counted as failures, but successful queries for unregistered names are not treated as failure.

## Dependencies
The benchmark depends on NBT asynchronous request APIs, tevent, socket binding, interface discovery, loadparm NBT port, the global `torture_entries`, and the target WINS server. It also depends on talloc lifetime rules: request private data is allocated under the socket and freed by handlers.

## Integration Points
`torture_bench_wins()` is registered under the NBT suite by `nbt.c`. The benchmark complements functional WINS tests in `wins.c` by applying concurrent-style pressure through up to ten outstanding async operations. It uses the same target resolution helper and progress setting convention as `query.c`.

## Risks
`generate_register()`, `generate_release()`, and `generate_query()` assume `nbt_name_*_send()` returns a non-NULL request before assigning callbacks; allocation or send setup failure could dereference NULL. If `torture_entries` is zero, modulo by zero will occur. Because releases are random and TTL is only bounded by the run time, failed/early runs can leave WINS records behind until expiry. The benchmark does not validate returned query addresses, only status relative to local registered state.

## Test Signals
Signals are final operations-per-second output, failure count, progress every fifty sends when enabled, and complete draining of outstanding async requests. Important edge tests include `torture_entries=1`, larger pools, timeout-heavy servers, request allocation failure handling, and post-run WINS cleanup checks.
