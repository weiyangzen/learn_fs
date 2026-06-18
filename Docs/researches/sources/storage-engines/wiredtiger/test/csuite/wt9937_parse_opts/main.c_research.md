# sources/storage-engines/wiredtiger/test/csuite/wt9937_parse_opts/main.c

## Purpose
WT-9937 unit-tests `testutil_parse_opts` and the extended parsing idiom using `testutil_parse_begin_opt`, `__wt_getopt`, `testutil_parse_single_opt`, and `testutil_parse_end_opt`.

## Important APIs, Types, and Functions
- Uses `TEST_OPTS` plus local `FICTIONAL_OPTS` and `SUBSET_TEST_OPTS`.
- `driver` contains simulated command lines and expected parsed fields.
- `check` chooses normal parsing when argv[0] is `parse_opts` and extended parsing when argv[0] is `parse_single_opt`.
- `verify_expect` compares actual options to expected values, with `NONZERO` used for generated seeds.
- `report` supports manual invocation output.

## Control Flow
With command-line arguments, the program expects `--parse_opts` or `--parse_single_opt`, rewrites argv[0] by skipping `--`, parses, reports changed fields, and cleans up. With no arguments, it iterates the driver table, builds expected `TEST_OPTS`, parses each synthetic command line, verifies expectations, and cleans up after each case.

## State and Persistence Behavior
No WiredTiger database state is created. Parser global state `__wt_optind` and `__wt_optreset` is reset before each simulated parse. `testutil_cleanup` is still called to release allocations in `TEST_OPTS`.

## Dependencies and Integration Points
The test targets shared test utility parsing, tiered-storage options (`-PT`, `-Po`, `-PS...`), build directory, thread count, verbose flag, and extended test-owned options.

## Risks and Test Signals
Failures reveal parser regressions in combined short options, attached/separate option values, tiered storage defaults, seed parsing, or handoff from test-owned options to testutil parsing. It intentionally verifies only a subset of `TEST_OPTS` fields.
