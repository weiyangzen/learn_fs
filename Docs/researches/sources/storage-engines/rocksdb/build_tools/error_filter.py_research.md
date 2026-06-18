# sources/storage-engines/rocksdb/build_tools/error_filter.py research

Purpose: `error_filter.py` reduces noisy CI/test output to known error lines for a named RocksDB test job. It reads merged stdout/stderr on stdin and prints matching error summaries.

Important APIs: `ErrorParserBase` defines the parser interface. `GTestErrorParser` tracks the most recent `[ RUN ]` test and reports GoogleTest failure locations. `MatchErrorParser` returns lines matching a regex. Specialized subclasses match compiler, scan-build, db crash, write stress, ASAN, UBSAN, Valgrind, compatibility, and TSAN errors. `_TEST_NAME_TO_PARSERS` maps CI job names to parser classes. `main()` validates the test name and streams stdin through parser instances.

Control flow: after argument validation, the script instantiates the parser list for the requested job. Each stripped input line is offered to each parser in order; any non-`None` parsed message is printed. `GTestErrorParser` updates internal last-test state on run lines and emits that test name on failure lines.

State and persistence: parser state is in memory only, primarily the last GoogleTest name. There are no file writes. Exit status is driven by `sys.exit(main())`; usage and unknown-test strings become nonzero process exits.

Dependencies and integration: it depends only on Python stdlib `re` and `sys`. It integrates with CI jobs that know their RocksDB job name and pipe test logs through this filter.

Risks and test signals: regexes are anchored and may miss format changes in tool output. Unknown job names produce an error instead of falling back to generic parsing. Stripping lines can alter spacing-sensitive diagnostics. Tests should feed representative logs for every parser class and verify output lines and unknown-job behavior.
