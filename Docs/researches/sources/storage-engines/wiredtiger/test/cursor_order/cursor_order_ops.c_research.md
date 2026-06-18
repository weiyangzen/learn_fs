# sources/storage-engines/wiredtiger/test/cursor_order/cursor_order_ops.c

## Purpose

`cursor_order_ops.c` is the concurrent workload engine for the WiredTiger `cursor_order` test. It creates per-thread workload descriptors, loads the target WiredTiger objects through `load`, runs reverse scanner threads and append writer threads against those objects, checks that reverse cursor traversal remains strictly descending while inserts are happening, verifies the resulting files, prints operation counts, and releases the run-local state.

The file focuses on an ordering invariant: after a cursor reset, repeated `cursor->prev` calls must not move forward or return keys outside the expected initial tail range. The workload stresses row-store string keys and variable-length column-store record numbers, with either one shared file or separate files selected by `SHARED_CONFIG`.

## Important APIs, types, and functions

- `INFO` is a file-local per-thread descriptor. It stores the target WiredTiger object URI, planned operation count, a `WT_RAND_STATE`, counters for append inserts and reverse scans, and a pointer back to `SHARED_CONFIG`.
- `run_info` is a file-local global array shared by `ops_start`, worker thread start functions, and `print_stats`.
- `ops_start(SHARED_CONFIG *cfg)` is the exported entry point declared in `cursor_order.h` and called by the main test driver. It allocates descriptors and thread IDs, prepares objects with `load`, starts threads, waits for completion, verifies with `verify`, prints timing/statistics, and frees memory.
- `reverse_scan_op` performs one bounded reverse cursor walk. It calls `cursor->reset`, loops up to `cfg->reverse_scan_ops`, calls `cursor->prev`, decodes the current key, and checks initial range and descending order.
- `reverse_scan` is the thread entry point for reader/scanner threads. It opens a snapshot-isolation session and cursor, repeatedly calls `reverse_scan_op`, closes the session, then sets `cfg->thread_finish`.
- `append_insert_op` appends one record by atomically incrementing `cfg->key_range`, setting row or column key format, formatting a `WT_ITEM` value, and calling `cursor->insert`.
- `append_insert` is the writer thread entry point. It opens a snapshot-isolation session and cursor, repeatedly calls `append_insert_op`, closes the session, then sets `cfg->thread_finish`.
- `print_stats` reports each thread descriptor's reverse-scan and append-insert counters.

The main external WiredTiger/test utility APIs are `WT_CONNECTION::open_session`, `WT_SESSION::open_cursor`, `WT_SESSION::close`, `WT_CURSOR::reset`, `WT_CURSOR::prev`, `WT_CURSOR::get_key`, `WT_CURSOR::set_key`, `WT_CURSOR::set_value`, `WT_CURSOR::insert`, `__wt_thread_create`, `__wt_thread_join`, `__wt_thread_str`, `__wt_yield`, `__wt_atomic_add_uint64`, `testutil_check`, `testutil_die`, `testutil_snprintf`, and `testutil_snprintf_len_set`.

## Control flow

`ops_start` first sizes `run_info` and `tids` to `cfg->reverse_scanners + cfg->append_inserters`. For each append writer slot it assigns the shared config, chooses or reuses an object name, optionally scales the operation count down by powers of two when `cfg->vary_nops` is set, and loads the object through `load`. In single-file mode all append threads share `run_info[0].name`; in multiple-file mode each append thread gets `file:cursor_order.%03d`.

It then configures reverse scanner slots after the append slots in `run_info`. Multiple-file scanners are mapped back to existing writer tables with `i % cfg->append_inserters`, so scanners read files that are also receiving writes. Single-file scanners share the first name. Any slot without a varied operation count falls back to `cfg->max_nops`.

After taking a wall-clock timestamp, `ops_start` starts reverse scanner threads first, passing IDs `0..reverse_scanners-1`, and then starts append writer threads for the remaining thread IDs. Each thread indexes `run_info` by the numeric argument. The function joins all threads, prints elapsed time and an operations-per-second estimate, verifies the files, prints per-thread counters, and frees names, the descriptor array, and the thread ID array.

`reverse_scan` initializes thread-local diagnostics and random state, yields once to let other threads start, opens a snapshot session and cursor on its assigned object, and loops until either `s->nops` reverse scans have run or `cfg->thread_finish` has been set by another thread. Each iteration yields after one `reverse_scan_op`. `append_insert` follows the same session/cursor lifecycle and loop shape for append inserts.

Inside `reverse_scan_op`, a cursor reset makes the next `prev` position the cursor at the end of the object. The function records `initial_key_range = cfg->key_range - cfg->append_inserters`, using a small offset to account for concurrent writers that may have reserved keys. For each `prev`, `WT_NOTFOUND` ends the scan, other errors are fatal, row-store keys are decoded with `atol`, column-store keys are read as integers, and two assertions are enforced: the first key must be at or above the initial range, and later keys must be strictly lower than the previous key.

Inside `append_insert_op`, `__wt_atomic_add_uint64` reserves a unique key number across all writers. Row-store keys are formatted as fixed-width decimal strings; variable-length column-store keys are passed as a record number. Values are short formatted buffers stored through a stack `WT_ITEM`, and `cursor->insert` persists the record.

## State and persistence behavior

The durable test state is in WiredTiger objects named by `FNAME` from `cursor_order.h`. Initial records are created by `load` in the companion file, and append operations add records through WiredTiger cursors. `verify` is called after threads stop to run WiredTiger verification against each represented object.

The key shared in-memory state is `cfg->key_range`, which tracks the current high key and is atomically incremented by append writers. Reverse scanners read it without a separate lock to establish an approximate expected tail range for their first `prev`; the test allows for concurrent writer reservations by subtracting `cfg->append_inserters`. `cfg->thread_finish` is a cooperative stop flag set by whichever reader or writer finishes its planned operation count first.

`run_info` owns per-thread counters and names for the duration of `ops_start`. In single-file mode multiple descriptors point at the same `run_info[0].name`, and the cleanup loop intentionally breaks after freeing the first name. In multiple-file mode each append slot owns a name allocation; scanner slots also allocate names containing the same URI text for target writer files, and all descriptor names are freed.

Sessions are opened with `isolation=snapshot`, so each thread uses WiredTiger transactional/session isolation while scanning or inserting. The code does not explicitly begin or commit transactions; it relies on autocommit cursor operations and session close to release resources.

## Dependencies and integration points

This file depends on `cursor_order.h` for `SHARED_CONFIG`, `FNAME`, `ROW`, `VAR`, `load`, and `verify`. The main test program in `cursor_order.c` initializes `SHARED_CONFIG`, opens the WiredTiger connection, and calls `ops_start` once per run. `cursor_order_file.c` implements object creation, bulk initial load, checkpoint, and verify.

The build integrates this file into the `test_cursor_order` executable with `cursor_order_file.c` and `cursor_order.c`. The smoke and CTest variants invoke the resulting binary with `-tr` for row-store and `-tv` for variable-length column-store coverage. The workload also depends on WiredTiger's internal thread, random, yield, and atomic helpers exposed through the test utility environment.

## Risks and edge cases

- Thread ID mapping is asymmetric: reverse scanner threads receive IDs starting at zero, but scanner descriptors were initialized at offsets after append descriptors. With default one-writer/five-scanner configuration, the first reverse scanner uses the append descriptor and the append writer IDs use scanner descriptors. This appears intentional only if all descriptors are interchangeable, but it makes counter labels and role-specific setup easy to misread and could be fragile when object-name ownership or varied operation counts change.
- `cfg->thread_finish` is written and read by multiple threads without an explicit atomic or lock in this file. It is a test stop flag, but data-race-sensitive toolchains may flag it.
- `reverse_scan_op` uses `atol` for row keys. The test's fixed-width numeric keys fit the expected positive integer format, but `atol` has weak error reporting if a malformed key appears.
- The initial range check depends on a non-locked read of `cfg->key_range` and subtracts only the append writer count. That models concurrently reserved inserts but is still approximate under scheduling delays.
- `append_insert_op` passes `(uint32_t)keyno` for non-row keys even though surrounding variables are `uint64_t`. The test's default ranges are small, but very large operation counts could truncate record numbers.
- The operations-per-second print multiplies the thread count by `total_nops`, even though `total_nops` is already the sum of per-thread operation counts. The value is diagnostic only, but it can overstate throughput.
- Snapshot sessions may make a scanner see a stable view that does not include later inserts, so the test validates reverse order within the visible view rather than requiring every new append to be visible.

## Test signals

Successful runs print per-thread start/stop lines, elapsed time, per-thread reverse scan and append insert counters, and complete without `testutil_die` or `testutil_check` failures. The most direct behavioral signal is that `reverse_scan_op` never reports "cursor scan start range wrong" or "cursor scan out of order". The final `verify` calls provide a storage-level integrity signal for each file touched by the workload.

Smoke coverage comes through `smoke.sh` and the CMake `check` variants, which run the executable as row-store (`-tr`) and variable-length column-store (`-tv`). Broader manual coverage is available through driver options such as multiple files, varied operation counts, scanner/writer counts, per-scan width, and repeated runs.
