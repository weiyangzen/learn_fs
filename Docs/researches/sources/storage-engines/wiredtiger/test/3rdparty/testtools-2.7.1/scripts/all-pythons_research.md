# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/scripts/all-pythons

Purpose: helper script to run the testtools suite across supported Python interpreters and emit a subunit stream.

Important APIs, types, and functions: `run_for_python(version, result, tests)` probes `python<version>`, emits skip if missing, sets local `PYTHONPATH`, launches `subunit.run`, feeds stdout to `TestProtocolServer`, and records stderr as an error detail. `now()` returns UTC timestamps. The main block creates a `TestProtocolClient` and iterates versions 3.7 through 3.12.

Control flow: for each version, the script first runs `pythonX -c pass` to detect availability. Available interpreters run selected tests or `testtools.tests.test_suite`; output is parsed into the aggregate result and stderr produces a synthetic error on a `PlaceHolder` test.

State and persistence: no intentional persistent state. It inherits environment, adjusts `PYTHONPATH` for child processes, and streams results to stdout.

Dependencies and integration points: depends on subunit, local testtools, multiple Python executables, and `testtools.content.text_content`. It integrates with CI systems that consume subunit.

Risks and test signals: uses `shell=True` for the availability probe, buffers all stdout/stderr in memory, and treats any stderr as a test error even if tests pass. Test signals are skips for missing interpreters and subunit result events for available ones.
