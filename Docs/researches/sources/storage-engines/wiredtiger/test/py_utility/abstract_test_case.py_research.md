# sources/storage-engines/wiredtiger/test/py_utility/abstract_test_case.py

Purpose: shared base harness for WiredTiger Python tests independent of a specific suite. It centralizes result output, stdout/stderr capture, test directory setup, deterministic random seeds, test identity formatting, known-failure helpers, and debugger/TTY support.

Important APIs and control flow: `TeeFile` mirrors writes to a capture file and optionally the original stream. `CapturedFd` tracks expected offsets in captured stdout/stderr and provides validators such as `check`, `checkAdditional`, `checkAdditionalPattern`, and `checkCustomValidator`. `AbstractWiredTigerTestCase` extends `unittest.TestCase`; setup methods initialize test directories and line-buffered result files, while `fdSetUp`/`fdTearDown` replace Python streams with tee captures. `failed()` adapts to several `unittest` outcome internals across Python versions.

State and persistence behavior: class-level state stores parent test directory, original streams, result file, random seeds, verbosity, preserved-file flags, and print-once markers. Per-test state stores capture file offsets and ignore regexes. It writes `results.txt`, `stdout.txt`, and `stderr.txt` under the configured test directory.

Dependencies and integration points: depends on `unittest`, file descriptors, `/dev/tty` for debug paths, and higher-level WiredTiger test cases that call `setupTestDir`, `setupIO`, `fdSetUp`, and `fdTearDown`. `suite_random` consumes the exported `getseed()`.

Risks: direct stream/file-descriptor manipulation is process-global and can be fragile under concurrent tests. `prout` writes through a duplicated stdout descriptor and expects it to remain valid. Captured output checks must keep ignore patterns current for expected verbose WiredTiger output.

Test signals: downstream tests rely on this harness to fail on unexpected stdout/stderr, preserve scenario names, emit PID-tagged logs, and report failure state correctly during teardown.
