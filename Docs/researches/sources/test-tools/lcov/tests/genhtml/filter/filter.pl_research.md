<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/filter.pl -->
# sources/test-tools/lcov/tests/genhtml/filter/filter.pl

- Purpose: Perl harness for lcov source filtering primitives: conditional detection, trivial-function detection, brace filtering, and compiler-directive filtering.
- Important APIs/types/functions: Uses `lcovutil`, `ReadCurrentSource`, `TraceFile`, `parseOptions`, `parse_ignore_errors`, `containsConditional`, `containsTrivialFunction`, `parse_cov_filters`, `write_info_file`, and `count_totals`.
- Control flow: Initializes options, checks `expr*.c`, mutates lookahead/bitwise globals, checks `*rivial*.c`, then compares vanilla, brace-filtered, and directive-filtered counts for `brace.c`.
- State and persistence behavior: Writes derived `.filtered`, `.orig`, and `.directive` files when matching `.info` inputs exist; global parser settings are reset between scenarios.
- Dependencies and integration points: Depends on repository lcov Perl modules, fixture source/info files, and current-directory glob order.
- Risks: Global settings can leak between checks, and broad globs can include unintended future fixtures.
- Test signals: Passing signal is final `passed` output with no `die`, plus expected count reductions in derived info files.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/filter/filter.pl -->
