# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/run.py

Purpose: command-line runner for executing or listing tests with testtools' extended result API.

Important APIs, types, and functions: `list_test()` returns runnable test ids plus import-error ids. `TestToolsTestRunner` implements `list()` and `run()` using `TextTestResult`. `TestProgram` subclasses `unittest.TestProgram` to add `--list`, `--load-list`, sorted discovery, failfast/catchbreak handling, stdout injection, and traceback-local capture. `main()` constructs `TestProgram`.

Control flow: `TestProgram.__init__` parses arguments, optionally filters the loaded suite by ids read from a UTF-8 file, then either runs tests or lists ids. `run()` wraps stdout with `unicode_output_stream`, starts/stops the result run, and executes the suite. Discovery sorts tests for deterministic order.

State and persistence: reads optional load-list files and writes results/listing to stdout. It clears `testLoader.errors` after setup. No persistent state is written.

Dependencies and integration points: depends on `unittest`, `TextTestResult`, `unicode_output_stream`, and `testtools.testsuite` helpers. Used by package Makefiles, CI, and `.testr.conf`.

Risks and test signals: code preserves compatibility fallbacks for runners that lack `tb_locals`, so constructor behavior can vary. Import errors affect list exit code. Test signals are `--list`, `--load-list`, failfast exit status, sorted discovery, and traceback-local capture.
