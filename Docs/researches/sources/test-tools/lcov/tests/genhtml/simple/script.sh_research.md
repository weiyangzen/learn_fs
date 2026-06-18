<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/simple/script.sh -->
# sources/test-tools/lcov/tests/genhtml/simple/script.sh

- Purpose: Primary genhtml integration harness for differential coverage: capture, version mismatch, fail-under, baseline/current/differential reports, owner tables, navigation, filtering, selection, criteria callbacks, path elision, spreadsheets, and unreachable exclusions.
- Important APIs/types/functions: Procedural shell script driven by `common.tst` variables such as `LCOV_OPTS`, `DIFFCOV_OPTS`, annotation/version scripts, criteria/select/unreachable callbacks, compiler flags, and optional MCDC support.
- Control flow: Compiles baseline/current variants, captures and gzips traces, creates diffs, renders many genhtml modes, verifies lcov substitution/exclude/trivial filters, tests callback criteria/selection, and checks expected error/ignore paths.
- State and persistence behavior: Creates many `.info/.gz`, `.json`, `.xlsx`, diff files, logs, annotation outputs, coverage databases, linked-path directories, and report trees; cleanup removes the named artifacts.
- Dependencies and integration points: Depends on C/C++ compilers, lcov/genhtml/geninfo, optional py2lcov/perl2lcov paths, Python modules, local `annotate.sh`, and stable HTML text anchors.
- Risks: Broad environment sensitivity: compiler branch layouts, optional MCDC, path mismatch heuristics, exact HTML strings, and optional tool availability.
- Test signals: Passing signals include expected HTML/source files, owner and truncation text, navigation HIT/MISS counts, criteria diagnostics, fail-under output preservation, spreadsheet generation, and expected malformed-option warnings.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/simple/script.sh -->
