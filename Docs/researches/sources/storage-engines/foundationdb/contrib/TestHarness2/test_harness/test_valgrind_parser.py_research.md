# sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/test_valgrind_parser.py

Purpose: tiny manual CLI harness for inspecting parsed Valgrind XML output.

Important APIs and control flow: imports `parse_valgrind_output`, parses the file path in `sys.argv[1]`, and prints each `ValgrindError` kind, primary backtrace, and auxiliary backtraces.

State and persistence: read-only input file, stdout output.

Dependencies and integration: depends on `test_harness.valgrind`; not a pytest/unittest despite the name.

Risks and test signals: no argument validation and no assertions, so it is a debugging utility rather than automated coverage. Useful smoke test for SAX parser output on captured Valgrind XML.
