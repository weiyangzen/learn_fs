# sources/user-network-fs/samba/source4/torture/raw/tconrate.c

## Purpose
`tconrate.c` is a benchmark-style torture worker that measures the rate at which an SMB server accepts tree connections. It repeatedly creates full SMB client connections to the configured host/share from multiple child processes and prints per-second and total connection rates.

## Important APIs, types, and functions
The exported entry point is `torture_bench_treeconnect()`. Helpers are `map_count_buffer()` for shared counters, `fork_tcon_client()` for child workers, `children_remain()` for nonblocking child reaping, and `rate_convert_secs()` for throughput calculation. It uses `smbcli_full_connection()`, `smbcli_tdis()`, `talloc_free()`, `lpcfg_smbcli_options()`, `lpcfg_smbcli_session_options()`, `samba_cmdline_get_creds()`, and resolve/gensec settings from the torture context.

## Control flow
The benchmark reads `host`, `share`, `timelimit`, and `nprocs` torture settings, maps shared integer counters, forks `nprocs` children, and has each child loop until its end time. Each child opens a full connection, disconnects the tree, frees the client state, increments its shared counter, and repeats. The parent wakes once per second, reaps finished children, computes the delta since the previous sample, prints connections per second, then prints total throughput after all children exit.

## State and persistence behavior
No filesystem data is intentionally created. State is process-local plus an anonymous/shared mmap counter array visible to forked children. Server-side effects are transient session/tree-connect churn, authentication load, and logs. The child exits directly with `exit(0)` after its loop or first connection failure.

## Dependencies and integration points
The file depends on POSIX `fork()`, `waitpid()`, `mmap()`, page-size APIs, Samba command-line credentials, loadparm, resolver context, GENSEC settings, and raw torture registration through `torture/raw/proto.h`. It is a benchmark rather than a pass/fail protocol validator, but it exercises connection setup, authentication, tree connect, and tree disconnect paths.

## Risks and edge cases
`map_count_buffer()` appears to round the buffer size with `(bufsz + pagesz) % pagesz`, which does not round up correctly and can produce a too-small mapping for some sizes. Counter updates are unsynchronized plain integer writes; approximate rates are acceptable, but strict accounting is not guaranteed. Failed child connections print an error and exit without propagating failure to the parent. Start times are intentionally unsynchronized, making runs noisy.

## Test signals
Useful signals are stable per-second output, successful child completion without connection failures, and plausible total connection rate over the configured time limit. Stress runs with larger `nprocs` should reveal authentication bottlenecks, connection leaks, or server-side tree-connect scalability problems.
