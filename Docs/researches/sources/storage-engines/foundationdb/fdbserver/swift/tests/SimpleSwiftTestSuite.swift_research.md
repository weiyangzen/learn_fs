# sources/storage-engines/foundationdb/fdbserver/swift/tests/SimpleSwiftTestSuite.swift

Purpose: Defines the minimal Swift async test harness used by fdbserver Swift/Flow interop tests. It gives tests a result-builder syntax, metadata, filtering, and a runner that executes all suites registered by `SimpleSwiftTestSuites`.

Important APIs/types/functions: `SimpleSwiftTestSuite` requires `init()` and a builder-backed `tests` list. `TestCasesBuilder.buildBlock` collects `TestCase` values. `TestCase` stores name, file, line, and an async throwing block, with `run()` invoking the block. `SimpleSwiftTestRunner.TestFilter` parses `--test-filter` and matches suite or test names. `SimpleSwiftTestRunner.run()` iterates registered suites and logs skip/test/pass/fail. `allTestsForSuite` and `findTestCase` locate tests by suite/name.

Control flow: The runner parses command-line arguments, iterates `SimpleSwiftTestSuites`, expands each suite by instantiating it, filters each test, and awaits `TestCase.run()`. Failures are caught and logged per test; the current implementation does not rethrow after a failed case, so the outer runner can still complete and signal its promise.

State and persistence behavior: Test metadata is immutable except `_testSuiteName`, which is currently unused. Runtime state is transient. No persistent storage is touched.

Dependencies and integration points: Depends on `SimpleSwiftTestSuites` from `swift_tests.swift` and color helpers from `Rainbow.swift`. The C++/Swift bridge entry point calls `SimpleSwiftTestRunner().run()` from a Swift `Task`.

Risks: Catching errors without propagating them can let a failing test suite complete successfully from the C++ promise perspective unless the failure is detected through logs or precondition crashes. The filter parser uses `fatalError` for missing values. The suite lookup uses stringification of type names, which is simple but brittle if module-qualified names change.

Test signals: Test signal is primarily console/trace text: `[skip]`, `[test]`, `[pass]`, `[fail]`. `findTestCase` offers a focused lookup path for future harness tests.
