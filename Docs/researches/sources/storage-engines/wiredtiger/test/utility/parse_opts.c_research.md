# sources/storage-engines/wiredtiger/test/utility/parse_opts.c

## Purpose
`parse_opts.c` initializes and parses the shared `TEST_OPTS` command-line structure used by WiredTiger C tests. It handles common options for home directories, thread counts, record/operation counts, table type, preservation, verbose mode, build directories, compatibility mode, in-memory mode, tiered storage, disaggregated storage, and deterministic random seeds.

## Important APIs and functions
The exported API is `testutil_parse_begin_opt`, `testutil_parse_single_opt`, `testutil_parse_end_opt`, and the convenience wrapper `testutil_parse_opts`. Internal helpers include `parse_number`, `parse_tiered_comma_separated_options`, `parse_tiered_artificial_errors`, `parse_tiered_artificial_delays`, `parse_tiered_random_seeds`, `parse_and_set_disagg_opt`, and `parse_tiered_opt`. The `EXPECT_OPTIONAL_ARG_IN_SUB_PARSE` macro adjusts WiredTiger getopt state for suboptions such as `-Pd` and `-Po`.

## Control flow and behavior
`testutil_parse_begin_opt` resets major `TEST_OPTS` fields, saves `argv`, sets `progname`, prints the command line, and builds a usage suffix from the caller's getopt string. `testutil_parse_single_opt` maps each option to a `TEST_OPTS` field. `-P` dispatches to tiered suboption parsing: `T` enables tiered storage, `S` parses `D`/`E` seeds, `d` and `e` parse artificial delay/error frequency plus milliseconds, and `o` validates `dir_store`. `testutil_parse_end_opt` supplies default home/progress/URI strings, fills default tiered source, deduces the build directory when extension loading is needed, and initializes two random states.

## State, dependencies, and integration
State lives entirely in `TEST_OPTS`; allocated strings are later released by `testutil_cleanup`. The parser depends on the WiredTiger getopt globals `__wt_optarg`, `__wt_optind`, `__wt_optopt`, and `__wt_optreset`, plus allocation and fatal helpers from `misc.c`. It integrates with `tiered.c`, `util_random.c`, disaggregated-storage config macros, and test binaries that either parse one option at a time or use the wrapper parser.

## Risks and test signals
Parsing uses `strtoll`/`atoll` with limited numeric validation, so malformed or overflowed input may not be rejected consistently. Tiered comma parsing rejects duplicated first values and too many comma values but has a typo in one `-PS` error message. Tests should cover default home/URI construction, seed reproducibility, tiered defaults after `-PT`, explicit build directories, usage output on unknown options, and correct extension build-directory deduction when tiered or disaggregated storage is enabled.
