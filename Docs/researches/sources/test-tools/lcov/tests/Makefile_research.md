# sources/test-tools/lcov/tests/Makefile

Purpose: top-level LCOV test Makefile that composes common test rules, runs all major test suites, and optionally builds coverage and performance reports from the test run.

Important targets/state: exports `COVER_DB`, `PYCOV_DB`, and `HTML_RPT` when `COVERAGE=1`; defines `all: check report`; includes `common.mak`; sets `TESTS := genhtml lcov llvm2lcov py2lcov perl2lcov xml2lcov`; defines `excel`, `info`, `report`, and `clean`.

Control flow and persistence: `excel` converts all JSON profiles to `report.xlsx`. `info` merges Devel::Cover databases, optionally emits per-test coverage info, converts Perl and Python coverage data to lcov info files, and preserves per-test artifacts when configured. `report` runs genhtml over produced info files with branch, annotation, version, and filter options. `clean` removes generated info/log/count/gcov/report/coverage artifacts and generated source.

Dependencies and integration: relies on variables and tools from `common.mak`, including `PERL2LCOV_TOOL`, `PY2LCOV_TOOL`, `GENHTML_TOOL`, `ANNOTATE_SCRIPT`, `VERSION_SCRIPT`, and `SPREADSHEET_TOOL`.

Risks and test signals: coverage targets are shell-heavy and assume Devel::Cover, Python coverage, and lcov converters are installed. Globs are intentionally tolerant. The main signal is `make check`; coverage reporting is an optional deeper signal with more environmental dependencies.
