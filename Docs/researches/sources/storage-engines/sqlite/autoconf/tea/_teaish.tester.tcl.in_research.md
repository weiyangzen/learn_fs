<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/autoconf/tea/_teaish.tester.tcl.in -->
# sources/storage-engines/sqlite/autoconf/tea/_teaish.tester.tcl.in

## Purpose
This is the template for the Tcl wrapper script invoked by teaish's `make test` recipe. It loads the extension DLL when one exists, sources teaish test utilities, optional package initialization/module scripts, and then runs extension test scripts or a default load-only smoke test.

## Important APIs, Types, And Functions
The script consumes three argv values: DLL name, Tcl `load` prefix, and path to `teaish/tester.tcl`. Conditional substitutions inject `TEAISH_VSATISFIES_CODE`, `TEAISH_PKGINIT_TCL`, `TEAISH_TM_TCL`, `TEAISH_TEST_TCL`, `TEAISH__DEFINES_MAP`, `TEAISH_NAME`, `TEAISH_VERSION`, and `TEAISH_TESTER_TCL`. It uses Tcl built-ins `llength`, `lindex`, `load`, `file normalize`, `lassign`, `source -encoding utf-8`, `apply`, `join`, and `array set`.

## Control Flow
The script optionally evaluates version-satisfaction code, loads the extension from a normalized path when argv0 is non-empty, removes the DLL and load-prefix args from `::argv`, sources the tester utility script, sources generated package init and Tcl module scripts if configured, and then sources each extension test file. Before each test script it populates `::teaish__BuildFlags` so test utilities can query build flags. If no test scripts are configured, it prints a default successful-load message.

## State And Persistence Behavior
It does not persist files. Runtime state changes are the loaded Tcl extension, rewritten `::argv`, local `dir` variables for sourced scripts, and global `::teaish__BuildFlags`. It deliberately normalizes the DLL path for platforms such as Haiku where a bare filename may not load.

## Dependencies And Integration Points
The file is generated and invoked from teaish `Makefile.in` test targets. It depends on Tcl, the built extension DLL when enabled, generated tester/test/pkginit/tm files, and teaish's tester utility API. Extension test files can rely on the loaded package and build flag array.

## Risks
Argument ordering must remain synchronized with `Makefile.in`'s `test-core.args`; otherwise the wrong script could be sourced or the wrong DLL loaded. Since sourced scripts run in the test process, bad generated paths or malicious test content execute directly. The load-prefix and Tcl version-satisfaction substitutions must match generated package metadata.

## Test Signals
The direct signal is `make test` under teaish. A successful no-test extension prints the default load message. Configured tests should observe a loaded extension, valid `::argv` after stripping teaish's internal args, and populated `::teaish__BuildFlags`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/autoconf/tea/_teaish.tester.tcl.in -->
