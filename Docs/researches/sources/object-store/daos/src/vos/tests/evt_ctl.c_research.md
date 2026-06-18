# sources/object-store/daos/src/vos/tests/evt_ctl.c

## Purpose
Command-line and cmocka test driver for the DAOS extent tree (`evtree`). It supports scripted tree operations, interactive command parsing, drain tests, sorting variants, and a substantial internal regression suite.

## Important APIs, types, and functions
- CLI helpers: `ts_open_create`, `ts_close_destroy`, `ts_add_rect`, `ts_delete_rect`, `ts_remove_rect`, `ts_find_rect`, `ts_list_rect`, `ts_many_add`, `ts_drain`, and `ts_cmd_run`.
- Parsing uses extent syntax like `lo-hi@epoch[.minor][-epr_hi][:value]`, with optional leading `-` for expected failure.
- Built-in tests cover iterator flags/deletion, find, variable data sizes, node order limits, aggregation checks, overlap splitting, root deactivate/allocation bugs, outer punch behavior, and dynamic root yield.
- Memory helpers allocate fake SCM addresses through `utest_alloc` and free via evtree descriptor callbacks.

## Control flow
`main` initializes logging, creates a PMEM-backed utest pool/root, then chooses interactive mode, internal tests (`-t`), or scripted command execution. Scripted execution maps getopt operations to `ts_cmd_run`, mutating a global tree handle. Internal tests use cmocka setup/teardown to create separate PMEM pools per test and then call evtree APIs directly.

## State and persistence behavior
Global state includes the utest context, umem attributes, evtree root, tree handle, selected feature flags, tree order, and command argv. Persistent test state is a PMEM file at `/mnt/daos/evtree-utest` for CLI mode and per-test `/mnt/daos/evtree-test-N` pools for internal tests. Inserted values are stored through fake BIO/SCM offsets and freed through callbacks unless the no-free callback is selected.

## Dependencies and integration points
Depends on `daos_srv/evtree.h`, BIO address helpers, `utest_common`, cmocka, command parser utilities, and DAOS logging/assertion helpers. Shell/Python wrappers invoke this binary for long scripted and stress patterns.

## Risks and edge cases
The parser is compact and permissive; malformed strings can produce confusing failures. Global CLI state makes operation ordering important. Some tests use random hole epochs and current time, so reproduction may require logs. Large data-size tests intentionally drive `-DER_NOSPACE`; environment pool size matters. Sorting feature selection is global and affects subsequent tree creation.

## Test signals
Signals include cmocka assertions, iterator-visible/covered/embedded ordering checks, find/delete result validation, memory increase/decrease tracking, expected aggregation return value `1`, node-order rejection, drain completion, and regression counts for historical allocation/root bugs.
