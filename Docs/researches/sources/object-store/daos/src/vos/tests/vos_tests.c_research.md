# sources/object-store/daos/src/vos/tests/vos_tests.c

## Purpose
Main launcher for the broader VOS unit-test suite. It initializes a standalone VOS instance, parses command-line options, dispatches selected test groups, or runs all VOS tests by default.

## Important APIs, types, and functions
- `FOREACH_OTYPE` enumerates object types used by I/O tests.
- `print_usage()` documents test selectors and common filters.
- `run_all_tests(keys)` runs timestamp, MVCC, punch model, pool/container, discard, aggregation, GC, DTX, ilog, checksum, WAL, evtree, tree, mark, and I/O suites.
- `main()` handles options such as `--pool`, `--container`, `--io`, `--all`, `--run_vos_cmd`, `--storage`, `--filter`, `--exclude`, `--force_csum`, and `--force_no_zero_copy`.

## Control flow
The program initializes DAOS debug, first parses global options affecting storage/filter/feature flags, defaults `vos_path` to `/mnt/daos`, initializes VOS, then resets option parsing and dispatches selected tests. If no specific suite is selected, it runs all tests. Finally it optionally runs a `vos_cmd` command, reports failures, finalizes VOS and debug, and returns failure count.

## State and persistence behavior
Global test state includes `vos_path`, checksum/no-zero-copy flags, GC setting, and the VOS self instance. Test suites create their own pools/containers and may persist files under the configured storage path during execution.

## Dependencies and integration points
Depends on cmocka, VOS internals, `vts_common.h`, DAOS debug, and many suite entry points implemented elsewhere. It also integrates `run_vos_command` from `vos_cmd.c`.

## Risks and edge cases
The filter code uses a stack buffer sized from `sizeof(optarg)`, which is pointer-size rather than string length and can be too small. Option parsing happens twice, so new options must be handled consistently in both passes. `otype` is compared to array size but negative values are not explicitly rejected.

## Test signals
Signals are nonzero failure count, per-suite cmocka output, successful VOS initialization/finalization, and final success or error message.
