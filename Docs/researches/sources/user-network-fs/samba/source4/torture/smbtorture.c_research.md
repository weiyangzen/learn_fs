# sources/user-network-fs/samba/source4/torture/smbtorture.c

## Purpose
`smbtorture.c` is the main executable entry point for Samba's smbtorture test runner. It parses command-line options, initializes Samba client configuration, loads torture modules, creates the torture context and output directory, resolves targets, lists or runs requested tests, and returns a process status based on torture results.

## Important APIs, Types, and Functions
Key helpers are `prefix_name()`, `print_test_list()`, `run_matching()`, `torture_run_named_tests()`, `torture_parse_target()`, `parse_dns()`, `print_structured_testsuite_list()`, `print_testsuite_list()`, `torture_print_testsuites()`, `usage()`, `max_runtime_handler()`, and `main()`. Global `use_fullname` controls subunit prefix behavior. The runner relies on `torture_root`, `torture_init()`, `torture_run_suite()`, `torture_run_tcase_restricted()`, and `torture_run_test_restricted()` from the torture framework.

## Control Flow
`main()` initializes talloc, Samba command-line parsing, popt options, loadparm, credentials, and optional restrictions from `--load-list`. It translates target profiles such as `samba3`, `samba4`, `win7`, `w2k16`, and `onefs` into `torture:*` loadparm settings that individual tests read. It sets an optional alarm for maximum runtime, loads an extra module if requested, otherwise calls `torture_init()` to initialize static and shared smbtorture modules.

Listing modes print suites or test names and exit. Normal execution seeds the PRNG, selects a UI backend (`simple` or `subunit`), creates a per-run output directory under `--basedir` or the current directory, initializes `struct torture_context`, calls `gensec_init()`, and either enters `torture_shell()` or parses the first positional argument as a binding/UNC target. It then runs each requested test expression through `torture_run_named_tests()`.

`torture_run_named_tests()` treats `ALL` specially and otherwise delegates to `run_matching()`. `run_matching()` recursively walks suite, testcase, and test nodes, matches names with `gen_fnmatch()`, reloads character conversion state before execution, optionally adjusts subunit prefixes, and runs only matching nodes. `torture_parse_target()` accepts UNC paths or DCERPC binding strings and stores host/share/binding settings for tests.

## State and Persistence Behavior
The runner stores process-wide settings in loadparm under the `torture` namespace and in global variables such as `torture_seed`, `torture_numops`, `torture_entries`, `torture_failures`, and `torture_numasync`. It creates a temporary per-run output directory and deletes it via `torture_deltree_outputdir()` before exit. It can also load extra dynamic modules and read restriction files.

## Dependencies and Integration Points
The file integrates popt, Samba command-line and credentials helpers, loadparm, event contexts, GENSEC, module loading, DCERPC binding parsing, readline shell support, and torture UI backends. It is the top-level consumer of `torture.c` registration and of all module init functions built into smbtorture.

## Risks
Target profile flags are compatibility policy: changing them can alter expected behavior across many tests. The final return code logic is subtle because a torture result return code can coexist with the local `correct` boolean. `parse_dns()` allocates strings with `strdup`/`strndup` and stores them as command-line settings without local frees, which is acceptable for process lifetime but not reusable library style.

## Test Signals
Signals include successful suite/test discovery, valid parsing of UNC or binding targets, subunit/simple result output, nonzero return on setup or test failure, unknown-test messages for unmatched expressions, and maximum-runtime termination through `SIGALRM`.
