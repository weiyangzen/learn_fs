<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/function/function.sh -->
# sources/test-tools/lcov/tests/genhtml/function/function.sh

- Purpose: End-to-end genhtml function categorization harness comparing baseline and current C++ revisions across called/not-called combinations, version insertion, aliases, and report generation.
- Important APIs/types/functions: Procedural shell script using `LCOV_BASE`, `VERSION_OPTS`, `LCOV_OPTS`, `DIFFCOV_OPTS`, symlinks to fixture sources, and `common.tst` tool variables.
- Control flow: Captures baseline called/no-call traces, verifies inserting version data into a trace without versions, captures current called/no-call traces, builds a diff, and runs genhtml for matrix combinations against gold output.
- State and persistence behavior: Creates symlinks, binaries, coverage data, `.info/.gz`, `.json`, `.xlsx`, diffs, logs, and output directories; clean removes them.
- Dependencies and integration points: Depends on C++ compiler, lcov/genhtml, Python `xlsxwriter`, diff/sed/perl normalization, common harness, and local gold files.
- Risks: Compiler function end-line metadata, generated static initializer symbols, and xlsxwriter availability can affect results.
- Test signals: Passing signals are matching version-inserted data, expected matrix reports, end-line/proportion handling when supported, and alias suppression behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/function/function.sh -->
