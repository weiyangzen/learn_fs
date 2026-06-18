# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/testcase.py

Purpose: extended `unittest.TestCase` implementation plus helpers for details, matchers, expected failures, fixture use, placeholder tests, cloning, attributes, skip decorators, and result decoration.

Important APIs, types, and functions: `TestCase` adds `assertThat`, `expectThat`, detail management, cleanup/on-exception hooks, matcher-backed assertions, `expectFailure`, unique ids, `useFixture`, and strict base `setUp`/`tearDown` upcall checks. Helpers include `run_test_with`, `gather_details`, `unique_text_generator`, `PlaceHolder`, `ErrorHolder`, `clone_test_with_new_id`, `attr`, `WithAttributes`, `skip`, `skipIf`, `skipUnless`, `ExpectedException`, `Nullary`, and `DecorateTestCaseResult`.

Control flow: `TestCase.run()` resets per-run state, constructs the configured `RunTest`, and delegates execution. Failures call `onException`, attach traceback content, map exception classes to result methods, and pass `getDetails()` to extended results. `expectThat` records a stacktrace detail and sets `force_failure` so the run fails after continuing. `useFixture` sets up fixtures, gathers fixture details on failures, and schedules cleanup/detail gathering.

State and persistence: per-test mutable state includes cleanups, unique counters, traceback id generators, setup/teardown flags, and details dict. Monkey patches and fixtures may mutate external process state but are scheduled for cleanup. No file persistence is performed by this module directly.

Dependencies and integration points: depends on `unittest`, `warnings`, matcher modules, content helpers, monkey patching, `RunTest`, result adapters, and optional `fixtures`. It is the central integration point between test code and result reporting.

Risks and test signals: subclasses must call `super().setUp()` and `super().tearDown()` exactly once or receive `ValueError`. `assertItemsEqual` directly aliases `unittest.TestCase.assertCountEqual`, so Python compatibility matters. Fixture error paths are complex. Test signals cover matcher details, cleanup order, skip/expected failure/unexpected success, fixture detail propagation, placeholders, cloning, and decorator behavior.
