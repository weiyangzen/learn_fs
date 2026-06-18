<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/wttest.py -->
# sources/storage-engines/wiredtiger/test/suite/helpers/wttest.py

Purpose: Central Python test harness for WiredTiger suite tests. It owns global suite setup, per-test directories, connection/session lifecycle, output capture expectations, hook platform APIs, rollback retry behavior, teardown cleanup, backup convenience, statistics helpers, and parallel suite execution.

Important APIs and types: `ReadonlySimpleNamespace`, `timeout`, `TestSuiteConnection`, `ExtensionList`, and `WiredTigerTestCase` are the main types. Important methods include `globalSetup`, `finalReport`, `setUpConnectionOpen`, `wiredtiger_open`, `setUpSessionOpen`, `open_conn`, `reopen_conn`, `transaction`, `setUp`, `tearDown`, `backup`, output expectation context managers, exception helpers, `retryEBUSY`, `compactUntilSuccess`, `dropUntilSuccess`, `verifyUntilSuccess`, `checkpoint_and_verify_stats`, and module-level decorators/functions such as `open_cursor`, `longtest`, `extralongtest`, `prevent`, `skip_for_hook`, `only_for_hook`, `runsuite`, and `run`.

Control flow: `globalSetup` stores command-line variables, initializes hook manager, test directory, IO capture, randomness, and suite flags. `setUp` creates a unique test directory, enters it, opens a connection/session with statistics and extensions, and records the current testcase in thread-local storage. `_callTestMethod` wraps test execution with optional timeout and retries `WiredTigerRollbackError`. `tearDown` runs registered actions, hook teardown, optional layered verification, closes all tracked connections, validates captured output, deletes or preserves the directory, and reports failures.

State and persistence behavior: The harness creates `WT_TEST` subdirectories, `testname.txt`, `results.txt`, stdout/stderr capture files, and WiredTiger home files. `TestSuiteConnection` tracks open connections in `_connections` so teardown can close leaked handles. Static class state records seeds, verbosity, hook names, retry counts, and command-line vars.

Dependencies and integration points: Integrates with `abstract_test_case`, `test_result`, `wthooks`, `wtscenario`, WiredTiger Python bindings, `concurrencytest`, extension libraries under the build directory, and hook platform APIs for tiered/disagg/timestamp behavior.

Risks: It relies heavily on global/class state and thread-local current testcase, so parallelism and hooks must be disciplined. Output checking can create secondary failures after a primary error unless ignored. Retry-on-rollback hides transient failures but reports excessive aggregate retry rates. Extension config construction is string-sensitive.

Test signals: Suite result status, captured stdout/stderr checks, teardown action return tuples, connection-close success, layered verification, statistics deltas, retry counters, and preserved directories on failure are the key signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/wttest.py -->
