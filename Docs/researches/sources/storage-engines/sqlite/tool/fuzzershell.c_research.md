# sources/storage-engines/sqlite/tool/fuzzershell.c

## Purpose
`fuzzershell.c` is a specialized SQLite shell for fuzzing. It reads SQL test cases from stdin or files, executes them against isolated in-memory SQLite databases by default, supports multi-case corpus files, adds fuzzing-friendly SQL helpers, detects memory leaks after each case, and can run simulated OOM loops.

## Important APIs, Types, and Functions
`GlobalVars` stores program name, original and OOM memory methods, OOM counters, and current test name. `oomMalloc()` and `oomRealloc()` wrap SQLite memory allocation to simulate failures. `abendError()` aborts to signal fuzzer crashes; `fatalError()` exits normally. `sqlexec()` executes required setup SQL. Logging, trace, and exec callbacks provide verbose or quiet output.

The `Str` accumulator supports dynamic SQL text from `autoexec`. The embedded `eval()` implementation uses `EvalResult`, `callback()`, and `sqlEvalFunc()` to run recursive SQL. The embedded `generate_series` virtual table uses `series_cursor`, `seriesConnect()`, `seriesBestIndex()`, `seriesFilter()`, and related cursor methods. `integerValue()` parses decimal, hex, and size-suffixed options. `main()` owns option parsing, SQLite global configuration, input loading, test-case splitting, per-case database setup, execution, OOM iteration, unique-case storage, and cleanup.

## Control Flow
Startup shuts SQLite down, parses options such as memory heap/pagecache/lookaside/scratch settings, `--database`, `--oom`, `--unique-cases`, encodings, verbosity, and input files. It configures SQLite before initialization, optionally installs OOM memory methods, opens an in-memory database for unique-case deduplication, and reads each input file fully into memory. It skips leading `#` header lines and splits test cases on `/****<...>****/` markers.

For each test case, it opens either the named on-disk database or an in-memory `main.db`, configures lookaside, trace, `eval()`, `generate_series`, length limits, encoding, page size, and autovacuum, then optionally replaces the SQL with concatenated `autoexec.sql` rows from the database. It executes the SQL with verbose row output or a no-op callback, closes the database, asserts no leaked SQLite memory unless collecting unique cases, and repeats with different OOM countdowns when `--oom` is active. At the end it can write unique cases ordered by execution time.

## State and Persistence
Default database state is per-test in memory and discarded after each case. `--database` uses a caller-supplied database file and may persist mutations. `--unique-cases` stores unique SQL blobs and timings in a temporary in-memory SQLite database, then writes a compact corpus file. Global SQLite allocator, pagecache, scratch, and log configuration are process-wide. The OOM counters mutate around each SQLite execution.

## Dependencies and Integration Points
The file depends on SQLite's C API, optional trace API, virtual table API, SQLite memory configuration API, and the C runtime. It integrates with external fuzzers such as AFL, SQLite test corpora, OOM testing, and regression minimization workflows.

## Risks
Input files are loaded fully into memory. OOM simulation only wraps `xMalloc` and `xRealloc`, leaving other allocator methods from the original structure. `--database` allows persistent disk writes, unlike the default memory mode. The shell intentionally omits dot commands for safety, but arbitrary SQL can still exercise expensive or recursive behavior. `source` of SQL from an `autoexec` table means fuzzed databases can control executed SQL. The leak check depends on SQLite memory accounting and is skipped when unique-case collection is enabled.

## Test Signals
Signals include zero errors across multi-case corpora, crash/abort on SQLite API misuse or leaks, deterministic `--unique-cases` output, `--oom` completion across single-failure and repeated-failure modes, verbose trace and row output, `generate_series` query behavior, `eval()` recursion behavior, and `TEST_FAILURE` environment simulation.
