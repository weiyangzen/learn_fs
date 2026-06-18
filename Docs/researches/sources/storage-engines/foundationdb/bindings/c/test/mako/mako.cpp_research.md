# sources/storage-engines/foundationdb/bindings/c/test/mako/mako.cpp

## Purpose
`mako.cpp` is the executable driver for FoundationDB's C/C++ Mako benchmark tool. It parses command-line workload configuration, configures the FDB C API, forks worker and statistics processes, runs synchronous or Boost.Asio-based asynchronous workloads, collects shared-memory counters, and prints human-readable and JSON reports. It supports `clean`, `build`, `run`, and `report` modes.

## Important APIs, Types, and Functions
- `ThreadArgs` packages process/thread ids, parent pid, immutable `Arguments`, shared-memory access, and the assigned `fdb::Database`.
- `createNewTransaction`, `setTransactionOptionsIfEnabled`, `cleanupNormalKeyspace`, `populate`, `runOneTransaction`, and `runWorkload` form the transaction execution path.
- `workerThread`, `runAsyncWorkload`, and `workerProcessMain` bridge workload logic to thread/process orchestration.
- `Arguments::Arguments`, `parseArguments`, `parseTransaction`, `Arguments::setGlobalOptions`, `Arguments::validate`, and `usage` define the CLI contract.
- `printStats`, `aggregateWorkerStats`, `maybeCaptureWarmupSnapshot`, `printWorkerStats`, `loadSample`, `printReport`, `statsProcessMain`, and `mergeSketchReport` define reporting and DDSketch merge behavior.

## Control Flow
`main` parses arguments, applies defaults, validates mode-specific invariants, handles report-only merging, creates POSIX shared memory, initializes a `shared_memory::Access` layout, then forks `num_processes` workers plus one stats process. Workers call `workerProcessMain`, select/set up the FDB API, launch one FDB network thread per process, create configured databases, and run either native worker threads or async workflow states. The parent waits for `readycount`, flips the shared `signal` from `SIGNAL_OFF` to `SIGNAL_GREEN`, later flips to `SIGNAL_RED` for timed or completed runs, and waits for children.

In run mode, `runWorkload` throttles per-thread TPS, creates a transaction per iteration, applies timeout/GRV-delay options, optionally tags or traces transactions, and delegates the configured operation sequence to `runOneTransaction`. `runOneTransaction` walks `opTable`, waits on futures, updates error counters, retries through `on_error` paths, commits when needed, and records sampled latency for operations, commits, and whole transactions. Build mode uses `populate` to partition rows across process/thread workers and commit batches.

## State and Persistence Behavior
The file writes no durable application data beyond benchmark operations in the target FDB cluster. It creates transient POSIX shared memory named `mako<pid>`, temp DDSketch files under `/tmp/makoTemp<pid>`, optional JSON reports, and optional exported sketch JSON. Shared-memory state includes signal, readiness, stop counts, throttle factor, worker counters, thread timers, and process timers. Cleanup guards unlink shared memory and remove temp sample directories after report generation.

## Dependencies and Integration Points
It depends on the local C++ wrapper `fdb_api.hpp`, Mako headers (`operations`, `stats`, `shm`, `utils`, `async`, `future`, `admin_server`, `logger`), POSIX `fork`/`mmap`/`shm_open`, Boost.Asio, fmt, RapidJSON, and the FDB client network APIs. It integrates with FoundationDB tracing, TLS, knobs, distributed tracer selection, client bypass/multi-version-client options, transaction timeouts, database-level timeouts, read-your-writes disabling, and transaction tag throttling.

## Risks
The driver has several operational risks: manual shared-memory layout must stay synchronized with `shm.hpp`; process failure paths rely on guards and `_exit`; temporary sketch loading silently skips malformed JSON; `strcpy`/`memcpy` option parsing is bounded mostly by validation and fixed arrays but still sensitive to oversized inputs; optional-argument parsing mutates `optarg`; `goto transaction_begin` and retry handling make transaction state transitions subtle; and async mode has a different worker-count interpretation than synchronous mode. Some JSON report writing is hand-assembled and can break if string fields contain unexpected quotes.

## Test Signals
This file is itself a benchmark/test utility rather than a unit test. Useful signals are successful execution of `mako --mode build`, `--mode run`, `--mode clean`, and `--mode report`; correct nonzero per-op counters; DDSketch export/import round trips; timeout tests for `--transaction_timeout_tx`/`--transaction_timeout_db`; async vs sync runs; and trace/tagging runs that confirm client options are accepted.
