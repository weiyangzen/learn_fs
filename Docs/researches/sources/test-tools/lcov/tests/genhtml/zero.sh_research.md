<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/zero.sh -->
# sources/test-tools/lcov/tests/genhtml/zero.sh

- Purpose: Creates genhtml output for `zero coverage` fixture data and validates summary counts and generated files.
- Important APIs/types/functions: No shell functions; accepts `--coverage` and `--verbose`, and relies on environment variables for input info files and expected counts.
- Control flow: Runs `$GENHTML $ZEROINFO`, captures stdout/stderr, validates exit status and clean stderr, calls `check_counts` with `$ZEROCOUNTS`, and ensures HTML files exist.
- State and persistence behavior: Creates `out_zero` and stdout/stderr logs; source inputs are not modified.
- Dependencies and integration points: Depends on `$GENHTML`, mkinfo-provided trace/count variables, `check_counts`, Perl Devel::Cover filtering, and `find`.
- Risks: Fixture-data or genhtml stdout wording drift can break count checks while rendering still works.
- Test signals: Passing signals are matching counts, empty stderr outside coverage mode, and at least one generated `.html` file.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/zero.sh -->
