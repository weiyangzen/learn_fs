# sources/test-tools/fio/init.c

## Purpose
Owns fio process and job initialization: global CLI options, job-file parsing, default option setup, thread-data allocation, shared-memory segment management, I/O engine loading, option fixups, random seed setup, log initialization, client/server command handling, and top-level option parsing.

## Important APIs, Types, and Functions
Externally visible functions include `free_threads_shm`, `init_rand_offset_seed`, `td_fill_rand_seeds`, `ioengine_load`, `parse_dryrun`, `add_job_opts`, `parse_jobs_ini`, `parse_cmd_line`, `fio_init_options`, `parse_options`, `options_default_fill`, and `get_global_options`. Major internal functions include `free_shm`, `add_thread_segment`, `expand_thread_area`, `get_new_job`, `put_job`, `fixup_options`, `setup_random_seeds`, `init_flags`, `make_filename`, `add_job`, `__parse_jobs_ini`, debug/usage helpers, and output-format parsing.

## Control Flow
`parse_options()` initializes global defaults, parses command-line switches, dispatches job files or client/server mode, frees temporary default resources, and verifies that jobs exist unless the invocation was help, dry-run, profile, backend, or client-only. CLI job options create or update a `thread_data`; job files create sections with `global` inheritance and optional includes. `add_job()` turns parsed options into runnable jobs: initializes flags, loads the engine, creates implicit files, seeds random generators, normalizes options, initializes flow/rate/ramp/steadystate/log state, prints job summaries, handles blktrace merging, and recursively expands `numjobs`.

## State and Persistence Behavior
Global process state includes output files, CLI mode flags, ETA/status settings, trigger paths, debug masks, backend/client status, job-section filters, default thread options, shared thread segments, and job counters. Thread data may live in SysV shared memory unless configured otherwise. `atexit(free_shm)` tears down engines, files, shared memory, triggers, options, locks, and global cleanup. Runtime persistence includes configured output files and per-job logs initialized by `setup_log()`.

## Dependencies and Integration Points
This file integrates most of fio: parser/options, `smalloc`, file hash, verify, profiles, server/client, idle profiling, file locks, steadystate, blktrace, I/O engines, logs, flow, random distributions, dedupe, zoned block device options, and OS helpers. `ioengine_load()` bridges parsed options to `load_ioengine()` and engine-specific option storage.

## Risks
`fixup_options()` is broad and order-sensitive; changes can silently alter legacy job semantics. Shared-memory segment allocation and cleanup must match process/thread execution modes. Recursive `numjobs` cloning duplicates files and engine option memory, so ownership bugs are possible. Command-line parsing has many early-exit paths that call `exit()` directly. Include-file parsing uses mutable buffers and relative path logic that can be fragile. Global variables make repeated parser invocations sensitive to stale state.

## Test Signals
Strong signals come from fio parser tests, command-line help/enghelp/cmdhelp tests, job-file include tests, client/server parsing tests, option compatibility matrices, random seed reproducibility tests, `numjobs` cloning tests, log naming tests, and sanitizer runs over parse-only and failing-parse cases.
