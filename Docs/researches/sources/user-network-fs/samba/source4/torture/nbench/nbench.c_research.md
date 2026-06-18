
# sources/user-network-fs/samba/source4/torture/nbench/nbench.c

## Purpose
`nbench.c` registers and drives the `bench.nbench` smbtorture test. It replays a NetBench-style client load file against an SMB server, optionally with multiple client processes, timing control, target throughput throttling, read-only suppression of mutating operations, and reconnect retries. It delegates individual SMB operations and throughput accounting to `nbio.c`.

## Important APIs, Types, And Functions
Important globals are `nbench_line_count`, `timelimit`, `warmup`, `loadfile`, `read_only`, and `nb_max_retries`. The `NB_RETRY(op)` macro retries an operation through `do_reconnect()` while the operation returns false. `do_reconnect()` calls `nb_reconnect()` until retries are exhausted, then exits via `nb_exit()`. `run_netbench()` is the per-client worker used by `torture_create_procs()`. It parses load-file lines into shell-style tokens, handles optional leading timestamps, maps textual or numeric NT status values, dispatches operation names to `nb_*` wrappers, and loops the load file until `nb_tick()` indicates completion. `torture_nbench()` reads torture settings, creates shared nbench state, establishes common setup directories, installs signal handlers, forks workers, and prints final throughput. `torture_nbench_init()` creates the `bench` suite and registers the `nbench` test.

## Control Flow
`torture_nbench()` reads settings such as `nprocs`, `readonly`, `nretries`, `timelimit`, and `loadfile`, computes warmup as five percent of runtime, initializes `nbio_shmem()`, resets `SIGCHLD`, arms `SIGALRM` for periodic statistics, and runs `run_netbench()` in multiple torture processes. Each worker calls `nb_setup()`, prepares a per-client name like `client1`, opens the load file, then repeatedly parses and executes operations. Recognized operations include create, close, rename, unlink, deltree, directory operations, path/file/fs queries, setfileinfo, find-first, reads, writes, locks, unlocks, flushes, and sleep. Once the timer marks workers done, the worker closes the file, removes shared `\\clients` state when appropriate, closes its SMB connection, and returns correctness status.

## State And Persistence
`nbench_line_count` is global progress state used in diagnostics and by `nbio.c`. Runtime settings are file-static and process-local. Persistent remote state includes the `\\clients` directory and all files/directories created by the replayed workload; cleanup is performed by `torture_setup_dir()` before execution and `smbcli_deltree()` after execution when not read-only. Load-file progress is not persisted; the file is rewound repeatedly until the time limit expires.

## Dependencies
This file depends on Samba torture infrastructure, `smbcli_state`, `torture_create_procs()`, settings accessors, the nbench `proto.h` API implemented by `nbio.c`, NTSTATUS parsing, string-list helpers, locale character checks, and SMB/raw operation wrappers. It also depends on a valid NetBench-format load file, defaulting to `client.txt`.

## Integration Points
The suite is registered under `bench.nbench`, and documented options in `smbtorture.1.xml` map to settings consumed here. `run_netbench()` integrates tightly with `nbio.c`: every operation wrapper updates shared counters, checks statuses, and manages handle mappings. `torture_create_procs()` provides concurrency; `SIGALRM` drives reporting through `nb_alarm()`.

## Risks
The parser assumes enough parameters for each recognized operation and can read beyond token bounds if the load file is malformed despite the minimal `i < 2` check. `asprintf()` allocation for `cname` is not freed. The retry macro mutates local `n`, so maintenance changes around the macro must preserve that variable. Read-only mode silently skips mutating operations, which changes workload semantics. Signal handling is process-wide and can interact with surrounding test harness code if expectations change. A failed worker can leave remote test data.

## Test Signals
Useful signals include correct parsing of textual and hex NTSTATUS values, failure on dbench v1 load files, reconnect retry logs, periodic throughput/latency output from `nb_alarm()`, final `Throughput` output, and remote cleanup of `\\clients`. Regression tests should use a small synthetic load file covering each dispatch branch, malformed status fields, read-only mode, and forced reconnects.
