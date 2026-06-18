# sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/valgrind.py

Purpose: SAX parser for Valgrind XML reports used by TestHarness2 summaries.

Important APIs/types: `ValgrindWhat`, `ValgrindError`, enum `ValgrindParseState`, `ValgrindHandler`, and `parse_valgrind_output`.

Control flow: SAX events push parser states for `<error>`, `<kind>`, `<what>`, `<auxwhat>`, `<stack>`, and `<ip>`. Text accumulates error kind/description and builds `addr2line -e fdbserver.debug ...` command strings from instruction pointers. Completed errors are appended to `handler.result`.

State and persistence: in-memory parse stacks only; reads one XML file.

Dependencies and integration: Python XML SAX, pathlib. `Summary.done()` consumes parsed errors and ignores leak kinds while treating other kinds as severity-40 failures.

Risks and test signals: state assertions make malformed or unexpected Valgrind XML fatal; only instruction-pointer stack data is captured; leak filtering is external. Test primary and auxiliary stacks, multiple errors, leaks, malformed XML, and byte/string character chunks.
