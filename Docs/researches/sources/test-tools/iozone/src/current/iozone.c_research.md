# Research: sources/test-tools/iozone/src/current/iozone.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-009240`: lines 1-7579, `Docs/researches/chunks/subset-b-009240_research.md`
- `subset-b-009241`: lines 7580-16679, `Docs/researches/chunks/subset-b-009241_research.md`
- `subset-b-009242`: lines 16680-25345, `Docs/researches/chunks/subset-b-009242_research.md`

## Chunk Research

### subset-b-009240: lines 1-7579

# sources/test-tools/iozone/src/current/iozone.c lines 1-7579

## Scope

This chunk covers the first 7,579 lines of `sources/test-tools/iozone/src/current/iozone.c`, the front half of the monolithic Iozone filesystem benchmark implementation. The file continues after this chunk, so this report describes only the visible chunk and calls out cross-chunk dependencies where behavior is declared or invoked here but implemented later.

## Purpose

The covered code initializes Iozone's portable benchmark runtime, parses the complete command-line surface, defines global state used by all benchmark modes, dispatches single-stream tests, implements auto-mode iteration, implements most of the multi-process/thread throughput orchestrator, defines timing/cache/data-verification helpers, and begins the single-stream write/rewrite benchmark implementation.

At a high level, this chunk turns user options into global flags and sizes, allocates aligned working buffers, decides between throughput, auto, speed-test, distributed-client, or one-shot benchmark execution, and funnels work into the function dispatch table or throughput worker functions. The later chunks contain many of the actual read/random/pread/pwrite/thread/distributed worker bodies referenced here.

## Important APIs, Types, and Constants

The source is heavily conditionalized for old Unix, Windows, large-file, direct-I/O, mmap, async-I/O, pthread, and distributed modes.

Key portability wrappers:

- `I_LSEEK`, `I_OPEN`, `I_CREAT`, `I_FOPEN`, `I_STAT`, `I_PREAD`, `I_PWRITE`, and `I_MMAP` map to 64-bit variants when `_LARGEFILE64_SOURCE` is available, otherwise to standard POSIX calls.
- `off64_t` is typedefed on platforms that do not provide it.
- `MAP_FAILED`, `MAP_ANONYMOUS`, `MAP_FILE`, `O_SYNC`, and `O_RSYNC` receive compatibility definitions for older or non-Linux targets.
- `MODE` records whether the build is compiled for 32-bit or 64-bit pointer/offset assumptions.

Important data types visible in this chunk:

- `struct child_stats`: shared-memory result/control cell for throughput children. Fields include `flag`, `walltime`, `cputime`, `throughput`, and `actual`.
- `struct runtime`: wall time, CPU time, and CPU utilization stored alongside report arrays for spreadsheet/report output.
- `struct client_command`: native in-memory command message sent from distributed master to clients.
- `struct client_neutral_command`: string-encoded portable version of `client_command`, constrained by comments to stay below 1448 bytes to avoid fragmentation.
- `struct master_command`: native client-to-master result/status message.
- `struct master_neutral_command`: string-encoded portable version of `master_command`.
- `struct size_entry`: linked-list node for file-size and record-size iteration lists.
- `struct child_ident`: distributed-mode registry entry for each client, including host/workdir/executable/file information, ports, socket indexes, and state.

Important constants and control values:

- Default benchmark sizing: `KILOBYTES`, `RECLEN`, `FILESIZE`, `NUMRECS`, `KILOBYTES_START`, `KILOBYTES_END`, `RECLEN_START`, `RECLEN_END`, `MULTIPLIER`.
- Limits: `MAXBUFFERSIZE`, `MINBUFFERSIZE`, `MAXSTREAMS`, `MAXTESTS`, `MAX_X`, `MAX_Y`, `MAXNAMESIZE`.
- Test indexes/masks: `WRITER_TEST`, `READER_TEST`, `RANDOM_RW_TEST`, `REVERSE_TEST`, `REWRITE_REC_TEST`, `STRIDE_READ_TEST`, `FWRITER_TEST`, `FREADER_TEST`, `RANDOM_MIX_TEST`, plus `PWRITER_TEST`, `PREADER_TEST`, `PWRITEV_TEST`, `PREADV_TEST` when available.
- Child barrier states: `CHILD_STATE_HOLD`, `CHILD_STATE_READY`, `CHILD_STATE_BEGIN`, `CHILD_STATE_DONE`.
- Distributed message commands: `R_CHILD_JOIN`, `R_STAT_DATA`, `R_FLAG_DATA`, `R_JOIN_ACK`, `R_STOP_FLAG`, `R_TERMINATE`, `R_DEATH`.
- Thread/child test codes: `THREAD_WRITE_TEST`, `THREAD_REWRITE_TEST`, `THREAD_READ_TEST`, `THREAD_REREAD_TEST`, `THREAD_STRIDE_TEST`, `THREAD_RANDOM_READ_TEST`, `THREAD_RANDOM_WRITE_TEST`, `THREAD_REVERSE_READ_TEST`, `THREAD_RANDOM_MIX_TEST`, `THREAD_PWRITE_TEST`, `THREAD_PREAD_TEST`, `THREAD_FWRITE_TEST`, `THREAD_FREAD_TEST`, `THREAD_CLEANUP_TEST`.

The `func[]` dispatch table maps single-stream test order to benchmark implementations:

- `write_perf_test`
- `read_perf_test`
- `random_perf_test`
- `reverse_perf_test`
- `rewriterec_perf_test`
- `read_stride_perf_test`
- `fwrite_perf_test`
- `fread_perf_test`
- `mix_perf_test`
- optional `pwrite_perf_test`, `pread_perf_test`, `pwritev_perf_test`, and `preadv_perf_test`

## Global State and Persistence Behavior

This chunk relies on a very large set of file-scope globals. The key behavior is not object-oriented; options and helpers mutate process-wide variables that are later consumed by benchmark loops and worker functions.

State categories:

- Sizing and iteration: `kilobytes64`, `reclen`, `numrecs64`, `min_file_size`, `max_file_size`, `min_rec_size`, `max_rec_size`, `r_range`, `s_range`, `t_range`, linked lists `size_list` and `rec_size_list`.
- Reporting: `report_array`, `report_darray`, `throughput_array`, `runtimes`, `current_x`, `current_y`, `max_x`, `max_y`, `Rflag`, `bif_flag`, `bif_filename`, `command_line`.
- Benchmark behavior flags: `aflag`, `trflag`, `include_tflag`, `include_test`, `include_mask`, `oflag`, `direct_flag`, `mmapflag`, `async_flag`, `verify`, `sverify`, `diag_v`, `dedup`, `dedup_interior`, `dedup_compress`, `noretest`, `notruncate`, `no_unlink`, `no_write`, `file_lock`, `rlocking`, `share_file`, `OPS_flag`, `MS_flag`, `cpuutilflag`.
- Buffer/cache state: `buffer`, `buffer1`, `mbuffer`, `mainbuffer`, `pbuffer`, `dedup_ibuf`, `dedup_temp`, `cache_size`, `cache_line_size`, `page_size`, `fetchon`, `purge`, `multi_buffer`.
- Throughput/parallel execution: `num_child`, `mint`, `maxt`, `childids`, `p_childids`, `barray`, `shmaddr`, `child_stat`, `stop_flag`, `stoptime`, `use_thread`.
- Distributed mode: `distributed`, `master_iozone`, `client_iozone`, `controlling_host_name`, `client_filename`, sockets/ports, `child_idents`, protocol buffers, and `proto_version`.
- Telemetry: `w_traj_flag`, `r_traj_flag`, trajectory file names, trajectory file descriptors, operation counts, byte counts, `compute_flag`, and `compute_time`.
- External side effects: temporary benchmark files, `.DUMMY` files, telemetry files, optional `wol.dat`/`rwol.dat`, Excel/report files, sockets, child processes/threads, shared memory, and optional external monitor commands.

Persistence is mostly via filesystem artifacts created during benchmarking:

- Main test file defaults to `iozone.tmp` or `-f`/`-F` filenames.
- Dummy files are built as `<filename>.DUMMY` or `<filearray[i]>.DUMMY.<i>`.
- `write_perf_test` opens `wol.dat` and `rwol.dat` when offset-latency output is enabled.
- Telemetry input/output files are opened by `open_w_traj()` and `open_r_traj()` declarations/uses.
- `record_command_line()` stores the command line in a static in-memory `command_line` buffer for later report output.
- Interrupt cleanup removes test files unless `no_unlink` is set and may dump Excel/throughput summaries before exit.

## Main Control Flow

### `main(argc, argv)`

`main` is the primary coordinator:

1. Initializes default filenames, stdout/stderr buffering, hostname, debug environment variables, random generation number, page size, clock ticks, file-name arrays, PID, external monitor command strings, splash lines, and signal handlers.
2. Allocates and cache-aligns the main I/O buffer and a dedup input buffer using `alloc_mem()`. It fills/touches dedup support state with `touch_dedup()`.
3. Initializes default filename and verification pattern. If no arguments are supplied, prints `USAGE` and exits with 255.
4. Parses options using `getopt()` with a large switch. Most options set globals and append splash text.
5. Parses `-+` extended options through a nested switch. This includes distributed mode, CPU utilization, diagnostics, multiplier, cluster host/port, no-retest, aggregate dataset, record/shared-file locking, existing-file read-only mode, short-circuit/compatibility data modes, dedup ratios/seeds, PIT timing server settings, histogram logging, and operation-rate limiting.
6. Finalizes timing resolution and optional speed-test mode.
7. Applies validation rules and incompatible-option checks, including telemetry limitations, throughput-vs-auto exclusion, `-f`/`-F` constraints, async-vs-mmap exclusion, missing async support, existing-file no-write restrictions, `-H`/`-k` exclusion, and dedup-vs-diagnostic exclusion.
8. Initializes record-size lists, prints resolution/cache/stride/process information, bounds record length to `MINBUFFERSIZE..MAXBUFFERSIZE`, and pre-fills/touches buffers for verification.
9. Optionally binds the parent thread to a CPU on supported platforms.
10. Chooses execution mode:
    - `multi_throughput_test(mint, maxt)` when throughput mode is enabled.
    - The immediately following `if (trflag && mint == maxt)` is effectively unreachable after the previous `trflag` branch because it already jumps to `out`.
    - `print_header(); auto_test();` for auto mode.
    - `print_header(); begin(kilobytes64, reclen);` for single-size mode.
11. Closes trajectory files, removes dummy file unless disabled, prints completion, warns about poor timer resolution, and dumps Excel output for non-throughput `Rflag`.

### `record_command_line()`

Prints the command line unless `silent`, and appends argv entries to `command_line` up to a fixed 1024-byte buffer. It reports truncation if the saved line would overflow.

### `begin(kilos64, reclength)`

Runs the single-stream benchmark dispatch table for a specific file size and record size.

Control flow:

1. Computes `num_tests` from `func[]`, subtracting optional tests not applicable to the current build or mode.
2. Handles `RWONLYflag`, flushes dirty data via two `sync()` calls, sets global `kilobytes64`, `reclen`, and `numrecs64`.
3. Stores file size and record size in the report arrays via `store_value()`, and prints the row prefix.
4. If specific tests were requested, calls only functions selected in `include_mask` and stores zero placeholders for skipped columns.
5. Otherwise calls every applicable function in `func[]`.
6. Emits newline, warns if write/read test timing was too fast, suggests a bigger file size, or suggests smaller record size after I/O failure.
7. Removes the main test file unless `no_unlink` is set.

### `auto_test()`

Implements automatic matrix testing:

1. Applies `-g`/`-n` max/min file-size overrides.
2. Rejects configurations where minimum record size exceeds minimum file size.
3. Sets crossover behavior, initializes file-size and record-size linked lists, and loops through every generated file size.
4. For large file sizes, it may skip small record sizes by switching `min_rec_size` to `LARGE_REC` and inserting dummy zero report entries for skipped record sizes.
5. For each record size that fits within the current file size, calls `begin(kilosi, recszi)`.

### `throughput_test()`

Implements most of the multi-child throughput workflow for one `num_child` setting. `multi_throughput_test()` is declared and is likely responsible for iterating `mint..maxt` in later lines.

Common pattern for each throughput subtest:

1. Allocate or reuse shared memory for `struct child_stats`.
2. Establish `stop_flag` either as `stoptime` in pthread mode or a slot at the end of shared memory in process mode.
3. Initialize child stats to `CHILD_STATE_HOLD`.
4. Optionally start external monitors and distributed-mode listener/client behavior.
5. Spawn one process/thread per child, using `start_child_proc()` for fork/distributed process paths or `mythread_create()` for pthread paths.
6. Parent waits until each child leaves `CHILD_STATE_HOLD`, sets `CHILD_STATE_BEGIN`, optionally staggers starts with `delay_start`, and signals distributed clients via `tell_children_begin()`.
7. Parent waits for process exit or thread join, or for distributed join messages.
8. Computes parent total time, corrects timer resolution edge cases, aggregates child `throughput`, `actual`, `cputime`, and maximum wall time.
9. Stores result values via `store_dvalue()` and optionally `store_times()`, prints child/parent throughput and min/max/avg per-child metrics, stops monitors, syncs, sleeps, applies rest delay, and tears down distributed listener/comm state.

Subtests visible in this chunk:

- Initial write: `THREAD_WRITE_TEST` / `thread_write_test`
- Rewrite: `THREAD_REWRITE_TEST` / `thread_rwrite_test`
- Read: `THREAD_READ_TEST` / `thread_read_test`
- Re-read: `THREAD_REREAD_TEST` / `thread_rread_test`
- Reverse read: `THREAD_REVERSE_READ_TEST` / `thread_reverse_read_test`
- Stride read: `THREAD_STRIDE_TEST` / `thread_stride_read_test`
- Random read: `THREAD_RANDOM_READ_TEST` / `thread_ranread_test`
- Mixed workload: `THREAD_RANDOM_MIX_TEST` / `thread_mix_test`
- Random write: `THREAD_RANDOM_WRITE_TEST` / `thread_ranwrite_test`
- Optional pwrite: `THREAD_PWRITE_TEST` / `thread_pwrite_test`
- Optional pread: `THREAD_PREAD_TEST` / `thread_pread_test`
- Fwrite: `THREAD_FWRITE_TEST` / `thread_fwrite_test`
- Fread: `THREAD_FREAD_TEST` / `thread_fread_test`
- Cleanup: `THREAD_CLEANUP_TEST` / `thread_cleanup_test`

The function uses `goto` labels (`next0` through `next10`) as skip points for include-mask filtering and optional feature availability. This makes the execution sequence stable but hard to modify safely.

### `signal_handler()`

Handles interrupt/termination:

- Distributed master runs `cleanup_children()`.
- The original master process removes the main file, per-child dummy files, and default dummy file unless `no_unlink`.
- Dumps Excel or throughput reports if requested.
- Emits timer-resolution warnings.
- Kills process-mode children on throughput runs.
- Closes trajectory files and speed-test sockets if open.
- Exits process with status 0.

## Data Pattern, Cache, and Timing Helpers

### `time_so_far()`

Returns elapsed wall time as a floating-point seconds value. Platform paths:

- Windows uses `QueryPerformanceFrequency()` / `QueryPerformanceCounter()` unless a PIT server is configured.
- OSF variants use `getclock(TIMEOFDAY)`.
- Other POSIX paths use `gettimeofday()` unless a PIT server is configured.

When `pit_hostname` is set, timing is delegated to `pit_gettimeofday()`, which is declared in this chunk and implemented later.

### `fetchit(buffer, length)`

Touches one byte per cache line to warm CPU cache lines for a buffer. It uses a volatile local array to discourage optimization away.

### `purgeit(buffer, reclen)`

Touches a corresponding range in `pbuffer` to make the target buffer cold relative to the CPU cache. It aligns the purge offset using `cache_size` and limits the number of cache lines to the smaller of the record and cache sizes.

### `prepage(buffer, reclen)`

Writes the benchmark pattern to one byte per cache line to fault pages in before timing, mainly to avoid copy-on-write or first-touch effects.

### `fill_buffer(buffer, length, pattern, sverify, recnum)`

Fills a buffer for write verification. Behavior changes by mode:

- Dedup mode calls `gen_new_buf()` using `dedup_ibuf` and returns.
- Diagnostic mode seeds `rand()` from `base_time + child-id + record-number` and generates evolving per-word data.
- Normal partial verification (`sverify == 1`) writes expected data only at page intervals.
- Full verification writes expected pattern or diagnostic pattern over cache-line-sized regions.

It also accounts for `share_file` by forcing the effective child id to zero so shared-file patterns are deterministic across children.

### `verify_buffer(buffer, length, recnum, recsize, patt, sverify)`

Validates a read buffer. Behavior mirrors `fill_buffer()`:

- `sverify == 2`: touches one word per page without checking.
- Dedup mode regenerates expected data with `gen_new_buf()` and compares a limited amount (`lite` is set to 1) to reduce validation overhead.
- Diagnostic mode reconstructs deterministic per-record pattern.
- `sverify == 1`: checks one word per page.
- `sverify == 0`: full cache-line walk and byte-level mismatch localization.

On mismatch, it prints file position, record number, record size, and expected/found values, then returns 1. Success returns 0.

## Write Benchmark Start: `write_perf_test()`

The chunk includes the first part of `write_perf_test(kilo64, reclen, data1, data2)`, which performs write and rewrite testing for single-stream mode. The function continues after this chunk.

Visible setup and open behavior:

- Determines `filebytes64` and `numrecs64` either from write telemetry (`w_traj_flag`) or from `kilo64 * 1024 / reclen`.
- Opens `wol.dat` and `rwol.dat` with headers when offset-latency logging is enabled by `Q_flag`.
- Builds open flags from `oflag`, optional `O_DSYNC`, read-sync flags, and direct-I/O flags.
- Contains a disabled/truncated sanity-check block guarded out by `#define FUSE`, intended to detect filesystems that fail a create/ftruncate/close/unlink sequence.
- Uses `noretest` to decide whether to run only write or both write and rewrite passes.
- Per pass, optionally records CPU/wall start times, purges buffer cache for remount mode, creates/truncates the file on first write pass unless `notruncate`, reopens with selected flags, and enables platform-specific direct I/O (`VX_SETCACHE` for VxFS or `directio()` on Solaris).
- Applies whole-file locking with `mylockf()` if `file_lock` is enabled.
- Initializes mmap file mapping via `initfile()` when `mmapflag` is set.
- Supports mixed mmap/file I/O by writing a page, seeking back, and syncing.
- Calls `fsync()` before timed operations and initializes async state when `ASYNC_IO` and `async_flag` are active.
- Warms and fills the main buffer before starting the timer.

The actual write loop and result storage are beyond line 7579 and must be covered by later chunk research.

## Dependencies and Integration Points

Internal functions declared or used here but implemented outside this chunk include:

- Benchmark implementations: `read_perf_test`, `random_perf_test`, `reverse_perf_test`, `rewriterec_perf_test`, `read_stride_perf_test`, `fwrite_perf_test`, `fread_perf_test`, `mix_perf_test`, `pread_perf_test`, `pwrite_perf_test`, `preadv_perf_test`, `pwritev_perf_test`.
- Thread workers: `thread_write_test`, `thread_rwrite_test`, `thread_read_test`, `thread_rread_test`, `thread_reverse_read_test`, `thread_stride_read_test`, `thread_ranread_test`, `thread_ranwrite_test`, `thread_mix_test`, `thread_pread_test`, `thread_pwrite_test`, `thread_fwrite_test`, `thread_fread_test`, `thread_cleanup_test`.
- Report helpers: `print_header`, `store_value`, `store_dvalue`, `store_times`, `dump_excel`, `dump_throughput`, `dump_cputimes`.
- Allocation and OS helpers: `alloc_mem`, `alloc_pbuf`, `purge_buffer_cache`, `mylockf`, `mylockr`, `mmap_end`, `initfile`, `async_*`, `do_compute`.
- Size/trajectory helpers: `init_file_sizes`, `get_next_file_size`, `init_record_sizes`, `get_next_record_size`, `open_w_traj`, `open_r_traj`, `w_traj_size`, `r_traj_size`, `traj_vers`, `get_traj`.
- Distributed-mode helpers: `start_child_proc`, `become_client`, `start_master_listen`, `start_master_listen_loop`, `wait_dist_join`, `tell_children_begin`, `stop_master_listen`, `cleanup_comm`, `cleanup_children`, `get_client_info`.
- Dedup/random helpers: `touch_dedup`, `gen_new_buf`, `init_by_array64`, `genrand64_int64`.

External dependencies:

- POSIX file APIs: `open`, `creat`, `close`, `read`, `write`, `fsync`, `ftruncate`, `unlink`, `lseek`, `stat`, `mmap`, `msync`, `sync`.
- Process/thread APIs: `fork` through `start_child_proc`, `wait`, `kill`, signals, pthreads, CPU affinity.
- Timing APIs: `gettimeofday`, `times`, platform-specific `getclock`, Windows performance counters, optional PIT socket time service.
- Networking APIs for distributed mode: sockets, `sockaddr_in`, DNS host lookup.
- Platform direct I/O APIs: `O_DIRECT`, `O_DIRECTIO`, VxFS ioctls, Solaris `directio`.
- Shell/popen integration: `uname -a` for `-M`, external monitor start/stop commands.

## Risks and Edge Cases

- The implementation is dominated by global mutable state. Many helpers depend on globals rather than parameters, making option interactions and distributed/thread behavior fragile.
- `main` uses unbounded `strcpy()` into fixed-size arrays for filenames, mount names, host names, telemetry names, and client filenames. Long user arguments can overflow buffers.
- `splash` is `80 x 80`, but many `sprintf()` calls can write more than 80 characters into a row, which is an overflow risk.
- The `-F` filename loop decrements `optind` and then reads `maxt` names, depending on `-t` having initialized `maxt` correctly. Off-by-one or insufficient-argument handling is brittle.
- The branch `if(trflag && (mint == maxt))` after an earlier unconditional `if(trflag) { multi_throughput_test(); goto out; }` appears unreachable in this chunk.
- Throughput orchestration repeats large blocks with manual `goto` labels, making it easy for fixes in one subtest path not to reach others.
- Parent/child synchronization uses shared-memory integer flags and polling with `Poll(1)`. There is no explicit memory-ordering primitive visible in this chunk beyond `VOLATILE`, which is not a complete cross-process/thread synchronization model on modern compilers/CPUs.
- Timer correction subtracts `time_res` and clamps to `time_res`; short tests can still produce misleading throughput and set `res_prob`.
- Direct I/O, mmap, async, locking, telemetry, and verification modes interact with strict constraints. The chunk rejects some invalid combinations, but more combinations are likely handled only by lower-level code.
- Dedup verification intentionally compares only a tiny slice in `lite` mode, which reduces overhead but can miss corruption outside the sampled word.
- `sync()` and `sleep(2)` are used as cache/settling controls; behavior is platform-dependent and can dominate small tests.
- Existing-file read-only mode (`-+E`) disables writes, verification, unlink, and requires explicit test selection, but write tests are rejected via hard-coded test indexes. Future dispatch-table changes would need synchronized updates.
- Some declarations use K&R compatibility and weak prototypes when `HAVE_PROTO`/`HAVE_ANSIC_C` are absent, increasing the chance of ABI/type mismatch on modern systems.
- The disabled sanity check is force-disabled by `#define FUSE` inside the function, so filesystem create/truncate correctness is not tested in this build path.

## Test Signals

Useful signals for validating this chunk:

- CLI parsing smoke tests:
  - `iozone -h` prints help and exits 0.
  - `iozone -v` prints version/header information and exits 0.
  - `iozone -s 64 -r 4 -i 0` reaches single-stream write dispatch.
  - Invalid combinations such as `-t 2 -f file`, `-a -F ...`, `-H 1 -k 1`, `-B -H 1`, telemetry plus auto mode, and no-write plus write tests should exit with documented errors.
- Auto-mode tests:
  - `-a -n <min> -g <max> -y <minrec> -q <maxrec>` should iterate file/record sizes and reject record size greater than file size.
  - Large file sizes should trigger crossover zero-fill report placeholders when applicable.
- Throughput tests:
  - `-t 2 -F file1 file2 -i 0 -i 1` should spawn two processes by default and aggregate child `child_stats`.
  - `-T -t 2 -F file1 file2 -i 0` should use pthread creation when threads are enabled.
  - Include masks should skip unselected subtests and preserve report-column placeholders.
- Cleanup behavior:
  - Normal completion removes `iozone.tmp` and `.DUMMY` files unless `-w`/`no_unlink`.
  - SIGINT/SIGTERM should remove temporary files, close trajectory files, and kill process-mode throughput children.
- Verification paths:
  - `-V <pattern>` should fill and verify data and label measurements invalid.
  - `-+d` diagnostic mode should produce deterministic per-record patterns.
  - `-+w`, `-+y`, and `-+C` should activate dedup buffer generation without diagnostics.
- Reporting:
  - `-R` should populate report arrays and call Excel dumping at normal exit or interrupt.
  - `-Q` should create `wol.dat` and `rwol.dat` headers in write paths.
- Platform/feature compile coverage:
  - Build variants with and without `HAVE_PREAD`, `HAVE_PREADV`, `NO_THREADS`, `ASYNC_IO`, `_LARGEFILE64_SOURCE`, `Windows`, and direct-I/O macros should compile because this chunk has many conditional prototypes and dispatch-table shapes.

## Cross-Chunk References

The following items are central to behavior visible here but are outside lines 1-7579:

- Completion of `write_perf_test()` write/rewrite loop and result storage.
- All read, random, reverse, stride, stdio, pread/pwrite, vector-I/O, and mixed workload single-stream functions.
- Worker thread/process functions used by `throughput_test()`.
- `multi_throughput_test()` and the per-child implementations that write `child_stats`.
- `alloc_mem()`, shared-memory allocation details, and thread wrapper details.
- Distributed-mode socket protocol implementation.
- Excel/report output serialization.
- Trajectory parsing and PIT timing implementation.
- Dedup buffer generation and Mersenne Twister functions.

### subset-b-009241: lines 7580-16679

# sources/test-tools/iozone/src/current/iozone.c lines 7580-16679

Chunk `subset-b-009241` covers a large middle section of Iozone's benchmark driver. It begins in the tail of the normal sequential write test, then defines single-process stdio, raw, random, reverse, record-rewrite, stride, positional, and vector I/O benchmark routines, report/table helpers, shared-memory allocation and process helpers, throughput orchestration, cache purge support, and the first group of threaded or child-process throughput workers. The chunk ends inside the setup path of `thread_stride_read_test()`, so that worker's actual stride loop and cleanup continue in a later chunk.

## Purpose

This section implements the benchmark operations that produce most of Iozone's per-record-size throughput cells:

- Buffered stdio write/read tests through `fwrite_perf_test()` and `fread_perf_test()`.
- Raw sequential read and write-family tests through the tail of `write_perf_test()` and all of `read_perf_test()`.
- Access pattern tests: random read/write, reverse read, rewrite-one-record, and stride read.
- Positional I/O tests, when compiled in: `pwrite_perf_test()`, `pread_perf_test()`, `pwritev_perf_test()`, and `preadv_perf_test()`.
- Reporting helpers that print headers, store measured values, and dump Excel-style throughput and CPU-utilization matrices.
- Memory/process helpers for shared allocations, sleeps, min/max, kill behavior, repeated throughput runs, and cache purging by unmount/remount.
- Thread/process worker routines for write, pwrite, rewrite, read, pread, reread, reverse read, and the setup of stride read throughput tests.

The code is controlled almost entirely by global options parsed elsewhere: direct I/O, mmap, async I/O, verification, dedup data patterns, trajectory files, operation-rate limiting, latency output, CPU accounting, file locking, record locking, cache purge, close/fsync inclusion, distributed-client operation, thread/process mode, and output format flags.

## Important APIs, Types, and Functions

Single-process benchmark routines:

- The leading boundary section is the end of `write_perf_test()`. It writes each record through mmap, async, no-copy async, Windows unbuffered `WriteFile()`, or POSIX `write()`, optionally driven by a write trajectory file. It records latency data to `wol.dat`/`rwol.dat`, histograms, operation counts, byte counts, and final write/rewrite rates.
- `fwrite_perf_test()` performs first write and re-write passes with `FILE *`, `I_FOPEN()`, `setvbuf()`, `fwrite()`, `fflush()`, `fsync()`, and `fclose()`. It returns early for mmap or async modes because stdio is not meaningful for those modes.
- `fread_perf_test()` performs first read and reread passes with `FILE *` and `fread()`, then verifies buffer contents when requested.
- `read_perf_test()` is the raw sequential read benchmark. It supports normal read, mmap copy, async read, no-copy async read, Windows unbuffered reads, read trajectory files, per-operation latency output, histograms, disruption hooks, direct I/O setup, file/record locking, and verification.
- `random_perf_test()` builds a random record order, preferably with a unique shuffled `recnum` array. Pass 0 randomly reads records; pass 1 randomly writes records unless `no_write` suppresses the write pass.
- `reverse_perf_test()` reads records from the end toward the start, using backward seeks for normal reads or direct offsets for mmap/async.
- `rewriterec_perf_test()` repeatedly rewrites the same record at offset zero while still counting the configured file-size worth of operations.
- `read_stride_perf_test()` reads through the file using a stride pattern based on global `stride`, `next64`, and wrap state. It measures how well storage handles non-contiguous but deterministic read access.
- `pwrite_perf_test()` and `pread_perf_test()` use `I_PWRITE()` and `I_PREAD()` to avoid changing the descriptor's file position. Both support trajectory-driven offsets and record sizes.
- `pwritev_perf_test()` and `preadv_perf_test()` use `pwritev()` and `preadv()` with the global `piov` vector array. `create_list()` supplies unique random offsets for vector elements, either through per-vector offsets when `PER_VECTOR_OFFSET` exists or a single base offset otherwise.

Report and utility helpers:

- `print_header()` emits the benchmark table header, choosing compact read/write-only, extended, or mmap/async-compatible layouts based on `Eflag`, `RWONLYflag`, `mmapflag`, `async_flag`, `HAVE_PREAD`, and `HAVE_PREADV`.
- `store_value()` writes one measurement into `report_array[current_x][current_y]`, advances `current_x`, and enforces `MAX_X`/`MAX_Y`.
- `store_times()` stores wall time, CPU time, and computed CPU utilization into the parallel `runtimes` matrix for the same logical cell.
- `dump_report()`, `dump_excel()`, `dump_times()`, and `dump_cputimes()` print stored matrices and, when `bif_flag` is active, also emit spreadsheet cells through `do_label()` and `do_float()`.
- `alloc_mem()` returns either ordinary heap memory, SysV shared memory, or anonymous/file-backed shared mmap memory depending on distributed/thread mode, `trflag`, `shared_flag`, `SHARED_MEM`, and platform macros.
- `Poll()` implements a short sleep with `select()`.
- `l_max()` and `l_min()` provide long-long min/max helpers.
- `Kill()` suppresses process termination when stonewalling is disabled through `xflag`.
- `multi_throughput_test()` runs `throughput_test()` over a child-count range or explicit `t_range`, updating the report grid after each run.
- `purge_buffer_cache()` unmounts and remounts `mountname` with retry loops to reduce filesystem-cache effects.

Thread/process throughput workers:

- `thread_write_test()` creates or opens the per-child output file, optionally truncates for mixed delete tests, waits for parent/master start, writes the file sequentially, and publishes `THREAD_WRITE_TEST` stats.
- `thread_pwrite_test()` is the positional-write variant. It pre-creates/truncates unless `notruncate` is set, then writes each record via `I_PWRITE()` or the async/mmap equivalents, publishing `THREAD_PWRITE_TEST`.
- `thread_rwrite_test()` rewrites an existing per-child file sequentially and publishes `THREAD_REWRITE_TEST`.
- `thread_read_test()` reads a per-child file sequentially, with optional read trajectories, verification, disruption, latency output, and `THREAD_READ_TEST` stats.
- `thread_pread_test()` is the positional-read variant. It uses `I_PREAD()` for normal I/O and also supports async/mmap paths.
- `thread_rread_test()` repeats the read path for reread statistics and publishes `THREAD_REREAD_TEST`.
- `thread_reverse_read_test()` seeks to the final record and reads backward, maintaining both descriptor position and a `current_position` value for mmap/async verification. It publishes `THREAD_REVERSE_READ_TEST`.
- `thread_stride_read_test()` begins in this chunk. The visible portion chooses child identity, CPU binding, per-child filename, read/direct flags, Windows unbuffered handle, `I_OPEN()`, async setup, VxFS/Solaris direct-I/O setup, and mmap setup; its actual stride loop is outside this chunk.

## Control Flow

The single-process benchmark routines follow a common pattern:

1. Compute `numrecs64` and `filebytes64`, optionally replacing them with trajectory file operation count and file size.
2. Build open flags from global settings such as `oflag`, `odsync`, `read_sync`, `direct_flag`, and platform-specific direct I/O flags.
3. Run one or two passes, depending on `noretest`. Pass 0 is the primary test; pass 1 is the repeat, rewrite, reread, or random-write side depending on the function.
4. Optionally purge cache with `purge_buffer_cache()`, open the target file, initialize async state or mmap state, prefetch buffers with `fetchit()`, seed fill patterns with `fill_buffer()`, and start wall/CPU timers.
5. Loop over records, optionally adjust offsets and record lengths from `get_traj()`, acquire record locks with `mylockr()`, burn synthetic compute time via `do_compute()`, rotate through `mbuffer` when `multi_buffer` is enabled, purge cache lines with `purgeit()`, execute the I/O operation, verify data with `verify_buffer()`, collect latency/histogram samples, and release locks.
6. End async queues with `end_async()`, flush/mmap-sync when requested, close or defer close according to `include_close`, subtract `time_res` and synthetic compute time, clamp tiny measurements to `time_res`, and store rates through `store_value()` and optional `store_times()`.

The rate calculation is consistent across routines. Normal throughput is bytes divided by elapsed time and then shifted from bytes/sec to KB/sec. `OPS_flag` reports operations/sec by using record counts. `MS_flag` reports microseconds per operation by calculating `1000000 * elapsed / operations`.

The threaded workers follow the same structure but add process/thread orchestration. Each worker derives a slot `xx` from the thread argument or global `chid`, optionally binds the thread to a CPU, selects a per-child filename from `filearray[]` with `share_file` and `mfflag` rules, initializes `struct child_stats` in `shmaddr[xx]`, marks itself `CHILD_STATE_READY`, then waits either for distributed master commands (`tell_master_ready()`, `wait_for_master_go()`) or for the parent to set `CHILD_STATE_BEGIN`. On completion or controlled stop, workers set throughput, actual work completed, CPU times, distributed stats, and `CHILD_STATE_HOLD`.

Stonewalling and stop behavior are important. Many throughput workers set `*stop_flag` when one child finishes unless `xflag` disables that behavior. Write workers still try to complete the write even after a stop signal because later read workers need the full test file; they record the pre-stop completed amount but continue writing to avoid downstream read failures.

## State and Persistence Behavior

Persistent filesystem state is the benchmark target files and per-child throughput files. Single-process tests use global `filename`. Throughput workers use `filearray[xx]` directly under multi-file mode or append `.DUMMY.<slot>` otherwise; `share_file` forces multiple workers onto slot zero's file name. Several error paths unlink child files unless `no_unlink` is set.

Optional sidecar output files are created in the working directory:

- Single-process latency logs such as `wol.dat`, `rwol.dat`, `rol.dat`, and `rrol.dat` are opened elsewhere or in this chunk depending on test type.
- Thread workers create files such as `Child_<n>_wol.dat`, `Child_<n>_pwol.dat`, `Child_<n>_rwol.dat`, `Child_<n>_rol.dat`, `Child_<n>_prol.dat`, `Child_<n>_rrol.dat`, and `Child_<n>_revol.dat` for latency traces.
- When `L_flag` is active, workers append start/finish timestamps to `Child_<n>.log`.

In-memory global benchmark state is extensive. This chunk reads and writes `report_array`, `runtimes`, `current_x`, `current_y`, `max_x`, `max_y`, `numrecs64`, `filebytes64`, `rec_prob`, `res_prob`, trajectory counters, random offset `offset64`, shared child stats in `shmaddr`, global stop flags, global buffers (`mainbuffer`, `buffer`, `mbuffer`, `barray`), and spreadsheet cursor state (`bif_row`, `bif_column`).

The mmap path persists dirty writes via `msync()` depending on `mmapasflag`, `mmapssflag`, `mmapnsflag`, `include_flush`, and final cleanup. The normal file path persists according to `fsync()` and `close()` inclusion options. The async path depends on `end_async()` to drain queued requests before measuring final state.

## Dependencies and Integration Points

This code integrates with the rest of `iozone.c` through many globals, macros, and helpers defined outside this chunk:

- Portability wrappers: `I_OPEN`, `I_CREAT`, `I_FOPEN`, `I_LSEEK`, `I_PREAD`, `I_PWRITE`, and platform macros for Windows, HPUX, Linux, AIX, IRIX, FreeBSD, DragonFly, TRU64, Solaris, VxFS, and SysV shared memory.
- Async I/O helpers: `async_init()`, `async_write()`, `async_write_no_copy()`, `async_read()`, `async_read_no_copy()`, `async_release()`, and `end_async()`.
- Mmap helpers: `initfile()`, `mmap_end()`, and `fill_area()`.
- Verification and data-pattern helpers: `fill_buffer()`, `verify_buffer()`, `pattern`, `sverify`, `dedup`, `dedup_interior`, `diag_v`, and `multi_buffer`.
- Timing and CPU accounting: `time_so_far()`, `utime_so_far()`, `stime_so_far()`, `cputime_so_far()`, `cpu_util()`, `time_res`, `cputime_res`, and `sc_clk_tck`.
- Locking and disruption: `mylockf()`, `mylockr()`, `disrupt()`, `disruptw()`, `file_lock`, `rlocking`, and `DISRUPT`.
- Trajectory support: `open_w_traj()`, `open_r_traj()`, `get_traj()`, `w_traj_*`, and `r_traj_*`.
- Reporting and spreadsheet helpers: `CONTROL_STRING*`, `create_xls()`, `close_xls()`, `do_label()`, `do_float()`, record-size list helpers, and include masks such as `WRITER_MASK`, `READER_MASK`, `PREADV_MASK`.
- Distributed throughput control: `tell_master_ready()`, `wait_for_master_go()`, `tell_master_stats()`, `send_stop()`, `client_error`, `client_iozone`, and `chid`.

The code also depends directly on OS APIs such as `read()`, `write()`, `fread()`, `fwrite()`, `fsync()`, `close()`, `fclose()`, `select()`, `mmap()`, SysV `shmget()`/`shmat()`/`shmctl()`, `system("umount ...")`, `system("mount ...")`, `pthread_setaffinity_np()`, VxFS `ioctl(VX_SETCACHE)`, Solaris `directio()`, and Windows `CreateFile()`, `ReadFile()`, `WriteFile()`, `SetFilePointer()`, and `CloseHandle()`.

## Risks and Edge Cases

- Many routines mutate `reclen` inside trajectory loops. Later calculations that recompute `filebytes64 = numrecs64 * reclen` can be wrong if a trajectory changed `reclen`; some write/read tests instead use trajectory byte and operation counters to compensate.
- Several no-copy async paths allocate an aligned buffer per operation and pass the original allocation pointer to the async layer. Correct cleanup depends on `async_write_no_copy()`/`async_read_no_copy()` and `async_release()`.
- Direct I/O requires alignment and size discipline. The code uses aligned buffers in no-copy paths and global buffers elsewhere, but any change to buffer allocation can break `O_DIRECT`/Windows unbuffered operation.
- Error handling is inconsistent by historical design: some paths call `signal_handler()`, some `exit()`, some `perror()` and continue only for stop-flag cases. This matters for automation because failures may terminate the whole process from deep inside a worker.
- `random_perf_test()` uses a shuffled record array if allocation succeeds, but falls back to pseudo-random draws that can repeat records. That changes the semantic from unique random coverage to sampled random access.
- `create_list()` uses a `goto again` collision loop and can become inefficient when `PVECMAX` approaches `numrecs64`; it relies on earlier clamping of vector count.
- Worker stop accounting subtracts the current record from completed KB/bytes when `*stop_flag` is set. With small `reclen` values below 1024, KB counters based on `reclen/1024` can lose sub-KB progress.
- `purge_buffer_cache()` builds shell commands by concatenating `mountname` into fixed-size buffers and invokes `system()`. It assumes trusted configuration and a mountpoint string that fits.
- `alloc_mem()` has several platform paths with temporary files and anonymous mmap. Some paths do not close temporary file descriptors in this chunk, relying on process cleanup or neighboring code assumptions.
- The per-thread CPU binding code differs by platform. `thread_pread_test()` only shows an HPUX binding block in this chunk, while other workers include Linux affinity handling.
- The read and reread workers sometimes report positional pread stats using `THREAD_READ_TEST` in distributed reporting, while local log names distinguish pread. That coupling needs care when interpreting distributed results.
- `thread_stride_read_test()` is incomplete in this chunk; any analysis of its runtime loop must be merged with the following chunk.

## Test Signals

Useful validation signals for this chunk include:

- Matrix output tests that compare column count and labels for normal, `-e` extended, read/write-only, mmap, async, `HAVE_PREAD`, and `HAVE_PREADV` builds.
- Throughput rate tests under normal KB/sec, `OPS_flag`, and `MS_flag`, including `noretest` cases where second-pass values should be zero.
- Verification-mode runs across write/read/rewrite/random/reverse/stride paths with `diag_v`, `dedup`, `dedup_interior`, and `multi_buffer` enabled.
- Trajectory-file runs for read, write, pwrite, and pread paths, checking variable offsets, sizes, latency output, operation counts, and byte totals.
- Async and no-copy async runs with verification enabled, confirming `async_release()` and buffer ownership paths do not corrupt data.
- Mmap runs with sync, async-sync, and no-sync options, checking `msync()` and cleanup behavior.
- Direct I/O runs on Linux, Solaris, VxFS, and Windows-unbuffered builds, especially with varying record sizes and alignment-sensitive buffers.
- File-lock and record-lock runs that exercise both read-lock and write-lock modes.
- Random access tests with file sizes smaller than `PVECMAX`, plus forced allocation failure or small-memory environments to cover random fallback behavior.
- Thread/process throughput runs with multiple child counts, `share_file`, `mfflag`, `xflag` stonewalling, distributed client mode, CPU-utilization reporting, per-child latency files, and operation-rate limiting.
- Failure-path tests for short read/write, missing files for reread/rewrite, direct I/O setup failure, inability to open sidecar logs, and cache-purge mount command failure.

## Chunk Boundaries

The chunk begins after the setup and opening portion of `write_perf_test()`, so final synthesis should merge it with the previous chunk to describe initial write flags, file creation, mmap initialization, and `wqfd` setup. It ends immediately after `thread_stride_read_test()` maps or opens the file; the stride-read wait, loop, verification, accounting, cleanup, and stats publishing continue in a later chunk.

### subset-b-009242: lines 16680-25345

# sources/test-tools/iozone/src/current/iozone.c lines 16680-25345

## Scope and Purpose

This chunk is the late implementation section of Iozone's monolithic benchmark driver. It starts inside the tail of `thread_stride_read_test()` and then covers mixed/random threaded workloads, cleanup, pthread wrappers, throughput report formatting, mmap/timing/locking helpers, telemetry file parsing, file/record size list construction, distributed master/client socket orchestration, network speed checks, pattern and dedup buffer generation, the embedded 64-bit Mersenne Twister, PIT remote-time support, latency histogram output, and stdio-based `fwrite`/`fread` benchmark variants.

The code is C implementation, not an isolated library module. Most functions depend on process-wide benchmark globals (`numrecs64`, `reclen`, `filearray`, `shmaddr`, `stop_flag`, `chid`, flags such as `direct_flag`, `mmapflag`, `async_flag`, `Q_flag`, `hist_summary`, `distributed`, and many more). The functions primarily integrate Iozone's worker lifecycle with OS file APIs, pthreads, sockets, timers, and optional platform features.

## Major Function Areas

### Threaded Workload Workers

- `thread_stride_read_test()` is already in progress at the chunk start. The visible tail performs strided reads using normal `read()`, mmap copy via `fill_area()`, or async reads. It records optional per-operation latency (`Child_<id>_strol.dat`), histogram samples, operation-rate pacing, record/file locks, verification, CPU utilization, and final child statistics in `struct child_stats`.
- `thread_mix_test()` selects each child as a reader or writer based on `pct_read`, `Kplus_flag`/`Kplus_readers`, or round-robin parity. It dispatches either sequential mix (`thread_read_test()`/`thread_write_test()`) or random mix (`thread_ranread_test()`/`thread_ranwrite_test()`).
- `thread_ranread_test()` opens each worker file read-only, optionally enables direct I/O, mmap, async I/O, and CPU affinity, then reads each record in a deterministic random order. It precomputes a shuffled `recnum` array when memory permits; otherwise it falls back to per-iteration random offsets. It updates throughput, `actual`, CPU time, wall time, histograms, `Q_flag` latency logs, and distributed master stats.
- `thread_ranwrite_test()` mirrors random reads for writes. It opens/creates the target file read-write, initializes mmap or async support, fills buffers for verification/dedup modes, writes records in shuffled order, and deliberately lets writers finish after a stop flag so concurrent readers do not observe short files. It tracks both byte and operation counts so `OPS_flag` can report operations/sec.
- `thread_cleanup_test()` removes each worker's dummy file when `no_unlink` permits it, participates in the same ready/begin barrier, sends distributed stats for `THREAD_CLEANUP_TEST`, marks its `child_stats` slot held, and exits.
- `thread_fwrite_test()` and `thread_fread_test()` implement stdio-buffered benchmark variants using `I_FOPEN()`/`fopen()`, `setvbuf()`, `fwrite()`/`fread()`, optional `fsync()`, verification, histograms, `Q_flag` latency logs, and the same distributed/statistics lifecycle. They return immediately when mmap or async mode is active.

Common worker control flow is: derive child id, optionally bind CPU, choose per-thread or process buffer, build the dummy filename, open/configure the file, initialize optional logs, set `child_stat->flag = CHILD_STATE_READY`, wait for parent/master begin, run the timed loop, flush/close if requested, compute throughput after subtracting `time_res` and optional compute delay, set shared stop semantics, send distributed results if needed, mark `CHILD_STATE_HOLD`, clean up logs/buffers, and exit or `thread_exit()`.

### Thread, Reporting, Mmap, and Timing Helpers

- `mythread_create()`, `thread_exit()`, `mythread_self()`, and `thread_join()` wrap pthread creation, exit, identity, and join. `NO_THREADS` builds retain stubs that print unsupported messages.
- `dump_throughput()` and `dump_throughput_cpu()` print matrix-style throughput/CPU reports and optionally write BIFF/XLS cells through `create_xls()`, `do_label()`, `do_float()`, and `close_xls()`. `store_dvalue()` stores report values into `report_darray[current_x][current_y]` and updates bounds.
- `initfile()` prepares files for mmap tests. When `flag` is set it preallocates/touches the file, with special handling for `O_DIRECT` files that cannot be sparse on Linux. It maps with `I_MMAP()`/`mmap()`, chooses shared/private flags from `prot`, and applies optional `madvise()`.
- `mmap_end()` unmaps mapped regions, and `fill_area()` copies between mapped file memory and the user buffer using `bcopy()`.
- Non-`ASYNC_IO` builds provide fail-fast async stubs (`async_read`, `async_write`, `async_init`, etc.) that print a message and exit if an async path is reached.
- `my_nap()` and `my_unap()` implement millisecond/microsecond pacing. `get_resolution()` and `get_rusage_resolution()` measure timer and CPU accounting granularity. `time_so_far1()` returns microseconds from Windows performance counters, OSF `getclock()`, local `gettimeofday()`, or PIT remote time.
- `cputime_so_far()` uses `getrusage(RUSAGE_SELF)` on Unix, while `cpu_util()` converts CPU/wall deltas into a percentage.

### Locking, Telemetry, and Size Lists

- `mylockf()` applies or releases whole-file advisory locks with `fcntl(F_SETLKW)` and `F_RDLCK`/`F_WRLCK`. `mylockr()` does the same for a byte range.
- `do_compute()` busy-waits for synthetic compute delay, and `disrupt()`/Windows `disruptw()` intentionally perturb read patterns by reading small pieces at the start and page-size offset before restoring the original file position.
- `get_traj()` reads the next non-comment telemetry line, accepting two fields (`offset size`) or three (`offset size delay_ms`) and returning offset while setting transfer size and delay. Invalid format or early EOF aborts through `exit()` or `signal_handler()`.
- `open_r_traj()`, `open_w_traj()`, `r_traj_size()`, `w_traj_size()`, and `traj_vers()` open/scan telemetry files, count operations, determine maximum file extent, and detect the number of fields in the first data row.
- `init_file_sizes()`, `add_file_size()`, `get_next_file_size()`, `init_record_sizes()`, `del_record_sizes()`, `add_record_size()`, and `get_next_record_size()` maintain simple linked lists of file and record sizes from explicit ranges or multiplicative defaults.

### Distributed Master/Client Protocol

The distributed mode is a custom TCP control protocol with two message families: `client_command` from master to child and `master_command` from child to master. For portability, `master_send()` and `child_send()` serialize numeric fields into neutral string structs (`client_neutral_command`, `master_neutral_command`); receive paths `sscanf()` the fields back into native structs.

- `start_master_listen()`, `master_listen()`, `stop_master_listen()`, `start_master_send()`, `start_master_send_async()`, `master_send()`, and `stop_master_send()` implement the master-side listener and outbound sync/async channels. They bind from configured base ports and increment until success.
- `start_child_listen()`, `start_child_listen_async()`, `child_attach()`, `child_listen()`, `child_listen_async()`, `child_send()`, `stop_child_listen()`, and `O_stop_child_send()` implement client-side listeners and messages to the master.
- `start_child_proc()` forks locally or calls `pick_client()` in distributed master mode. `pick_client()` launches a remote Iozone via `rsh`/`remsh` or `$RSH`, waits for join, creates sync and async channels, populates a `client_command` with benchmark configuration, sends it, and waits for the child ready barrier.
- `become_client()` is the remote child entry point. It daemonizes, starts sync/async listeners, sends a join message, receives and imports all benchmark state, changes to the assigned work directory, starts the async listener loop, computes telemetry extents if needed, and dispatches the requested worker by `testnum`.
- `tell_master_ready()`, `wait_for_master_go()`, `tell_master_stats()`, `tell_children_begin()`, `start_master_listen_loop()`, `start_child_listen_loop()`, and `wait_dist_join()` implement distributed barriers, result collection, and async stop propagation.
- `get_client_info()` and `parse_client_line()` parse the client identity file as `host workdir executable [file_name]`, with the optional fourth field enabling `mfflag`.
- `terminate_child_async()`, `distribute_stop()`, `send_stop()`, `cleanup_children()`, `cleanup_comm()`, and `child_remove_files()` handle normal completion, stop flag fan-out, interrupt/death cleanup, socket cleanup, and remote temporary file deletion.

Protocol state is carried through `child_idents[]` states such as `C_STATE_ZERO`, `C_STATE_WAIT_WHO`, and `C_STATE_WAIT_BARRIER`; shared-memory `child_stats` flags; `master_join_count`; generation marker `mygen`; and the process-shared `stop_flag`.

### Network Speed Check

The `speed_main()` family implements a separate distributed network throughput probe:

- `speed_main()` starts either a child-mode speed endpoint or forks a remote command with `-+t`.
- `sp_do_master_t()` measures master-to-child writes and child-to-master reads.
- `sp_do_child_t()` measures child-side receive and send loops.
- `sp_start_master_send()`, `sp_start_master_listen()`, `sp_start_child_send()`, and `sp_start_child_listen()` create one-off TCP channels for the speed test.
- `sp_send_result()` and `sp_get_result()` exchange formatted result records, and `do_speed_check()` runs the probe for each parsed client.

This is integrated with the same remote shell and controller host configuration as distributed Iozone, but uses separate `SP_*` port bases and result sockets.

### Patterns, Dedup, Randomness, PIT, and Histograms

- `get_date()` wraps `time()`/`ctime()` for log timestamps. `get_pattern()` derives the default byte pattern from `THISVERSION`, with `Z_flag` forcing legacy `0xa5` and `X_flag` forcing `PATTERN1`.
- `alloc_pbuf()` allocates and cache-size-aligns the purge buffer. `check_filename()` uses `I_STAT()` to verify a path is a regular file before unlinking.
- `start_monitor()` and `stop_monitor()` run optional external monitor commands from `IMON_START`/`IMON_STOP`, with foreground/background controlled by `IMON_SYNC`.
- `gen_new_buf()` transforms an input buffer into a configured mixture of dedupable, compressible, and non-dedupable regions. It uses seeds based on block number, child id/skew, total records, and `dedup_mseed`; `touch_dedup()` fills an initial buffer with deterministic random longs.
- The embedded MT19937-64 implementation provides `init_genrand64()`, `init_by_array64()`, `genrand64_int64()`, `genrand64_int63()`, and real-valued generators. Random read/write workers use it when `MERSENNE` is defined; otherwise they use `rand()` or `lrand48()`.
- PIT remote-time support (`pit_gettimeofday()`, `openSckt()`, `pit()`) mimics `gettimeofday()` by connecting to a remote service configured by `pit_hostname`/`pit_service`, reading a microsecond timestamp, and converting it into `struct timeval`.
- `hist_insert()` buckets operation latency into 40 microsecond-to-second ranges. `dump_hist()` appends per-child reports to `Iozone_histogram_child_<id>.txt`.

## State and Persistence Behavior

- Worker-visible state is mostly global and mutable. Benchmark flags imported by `become_client()` directly overwrite globals before the selected test runs.
- Child progress is persisted in shared memory through `struct child_stats` slots, especially `throughput`, `actual`, `cputime`, `walltime`, and `flag`.
- Stop behavior is cooperative. A child may set `*stop_flag`, call `send_stop()` in distributed mode, and continue or abort depending on workload semantics. Random writes specifically continue after a stop to keep reader-visible files complete.
- Temporary files are named from `filearray[]`, `.DUMMY.<id>`, `mfflag`, and `share_file`. Deletion is gated by `no_unlink` and `check_filename()` to avoid unlinking non-regular files.
- Optional outputs include per-child operation latency files (`Child_<id>_*ol.dat`), per-child start/finish logs (`Child_<id>.log`), histogram summaries (`Iozone_histogram_child_<id>.txt`), XLS/BIFF report output, and external monitor side effects.
- mmap tests persist file initialization by writing/touching file contents before mapping; `include_flush`, `include_close`, and mmap sync flags control when file data is synchronized or descriptors are closed.
- Distributed mode creates multiple TCP sockets and forked listener processes. It also relies on remote shell execution and remote working directories, so process/socket cleanup is part of benchmark correctness.

## Dependencies and Integration Points

- POSIX/Unix APIs: `open`/`read`/`write`/`close`, `lseek`, `fsync`, `fcntl` locks, `mmap`/`munmap`/`msync`, `madvise`, `gettimeofday`, `getrusage`, `times`, `select`, `usleep`, `nanosleep`, `fork`, `wait`, `kill`, `chdir`, `system`, `stat`, and sockets.
- Platform-specific paths: Windows `CreateFile`, `ReadFile`, `SetFilePointer`, `QueryPerformanceCounter`; HP-UX `prealloc` and processor binding; Solaris `directio`; VxFS `VX_SETCACHE`; OSF `getclock`; IRIX mmap flags; TRU64 direct I/O.
- Iozone-local wrappers and globals: `I_OPEN`, `I_FOPEN`, `I_LSEEK`, `I_MMAP`, `I_STAT`, `Poll`, `alloc_mem`, `purgeit`, `fetchit`, `fill_buffer`, `verify_buffer`, `signal_handler`, `purge_buffer_cache`, `create_xls`, `do_label`, `do_float`, `close_xls`, and numerous benchmark flags.
- Threading integration: pthread creation/join/exit and optional CPU affinity on Linux/HP-UX.
- Network integration: DNS resolution with `gethostbyname()`/`getaddrinfo()`, IPv4/IPv6 socket setup, fixed protocol command codes (`R_JOIN_ACK`, `R_CHILD_JOIN`, `R_STAT_DATA`, `R_FLAG_DATA`, `R_STOP_FLAG`, `R_TERMINATE`, `R_DEATH`), and configurable port bases.

## Risks and Edge Cases

- The code uses many unchecked `malloc()` results for per-worker filenames, telemetry random arrays, and stdio buffers. Some paths handle allocation failure (`recnum` fallback), while others assume success.
- Several fixed-size buffers are populated with `sprintf()`, `strcpy()`, and `strcat()` using filenames, hostnames, commands, and environment variables. Long paths or client file fields can overflow local arrays such as `tmpname[256]`, command buffers, or identity strings.
- Socket reads/writes generally assume whole neutral command structs or result payloads arrive in one or a few blocking calls. Partial writes, zero reads outside special async handling, interrupted syscalls, or network partitions can corrupt protocol progress or hang.
- Port binding loops increment indefinitely until bind succeeds. In exhausted or permission-limited port ranges this can spin for a long time.
- `start_master_listen()` retries bind inside a `while (rc < 0)` loop and has an unreachable post-loop `if(rc < 0)` check; similar patterns appear elsewhere.
- Distributed cleanup is state-sensitive. A child in `C_STATE_WAIT_WHO` lacks an async listener, while a barrier child has both sync and async processes; wrong state tracking can leave remote processes or files behind.
- `become_client()` imports remote config via `%s`, so paths with spaces are not supported and overlong fields can overflow command struct members.
- Random access tests seed PRNGs deterministically (`srand48(0)`, `srand(0)`, or fixed Mersenne seed array), which is good for repeatability but can produce identical access patterns across children unless other state changes the sequence.
- Direct I/O and mmap paths have strict alignment and sparse-file constraints; `initfile()` attempts to handle these but depends on `reclen` alignment and platform-specific flags.
- Histogram buckets are global and not reset in this chunk before each dump. In multi-test or multi-thread contexts, bucket reuse can contaminate later histogram output unless reset elsewhere.
- `my_unap()` truncates requested sleep to millisecond granularity before busy-waiting; very small or huge values can produce inaccurate pacing or CPU spin.
- `get_date()` copies `ctime()` output including its trailing newline into a fixed 30-byte buffer. Current ctime strings fit, but the API style is brittle.
- `check_filename()` returns false on stat failure and only unlinks regular files, protecting devices but also leaving failed-stat temporary files behind.
- The stdio tests open a separate descriptor only to `fsync()` before reads, then close it while using the `FILE *`; failures from this pre-read `I_OPEN()` are not checked before `fsync(fd)`.
- `gen_new_buf()` writes using `long *` across byte counts that may not be multiples of `sizeof(long)` and assumes sufficient alignment of the input/output buffers.

## Test Signals

- Random read/write tests should be run with verification, `Q_flag`, `hist_summary`, `OPS_flag`, `op_rate_flag`, `file_lock`, `rlocking`, `direct_flag`, `mmapflag`, async/no-copy modes, and distributed mode to exercise their divergent branches.
- Stop propagation should be tested with mixed readers/writers to ensure random writers finish file population while reported throughput/actual only count pre-stop work.
- Telemetry tests should cover comments, blank lines, two-field and three-field rows, invalid token counts, early EOF, max-offset calculation, and large offsets/sizes.
- Distributed tests should cover join, barrier, begin, stats, stop flag fan-out, terminate, death cleanup, protocol version mismatch, stale child generation (`mygen`) mismatch, and remote client errors.
- Socket robustness tests should force partial reads/writes, port collisions, slow accept/connect, and abrupt async-channel closure.
- mmap tests should cover `O_DIRECT` and non-direct file initialization, read-only/private versus write/shared mappings, `madvise` options, `include_flush`, `include_close`, and explicit mmap sync modes.
- Stdio `fwrite`/`fread` tests should verify direct and buffered `setvbuf()` modes, first-run file creation versus retest open behavior, `include_flush`/`include_close`, verification failure, and `restf` delay.
- Histogram tests should confirm bucket boundaries, per-child output naming, and whether buckets are reset between tests in the wider file.
- Dedup generation tests should compare expected identical, child-local, and randomized buffer regions across `dedup`, `dedup_interior`, `dedup_compress`, `chid_skew`, and `dedup_mseed` settings.
- PIT/time tests should cover local fallback, remote service success, DNS failure, socket failure, malformed PIT responses, and behavior under Windows and Unix timing paths.

## Cross-Chunk Notes

- The chunk begins inside `thread_stride_read_test()`, so that function's setup and initial open logic are defined in the previous chunk.
- Many worker functions invoked here (`thread_write_test`, `thread_read_test`, `thread_pwrite_test`, `thread_pread_test`, reverse read, reread, rewrite, async implementations, and buffer verification/fill helpers) are defined outside this line range.
- This chunk ends at the close of `thread_fread_test()`. Any following tests or final program teardown continue in later chunks.
