# sources/test-tools/lcov/tests/xml2lcov/xml2lcov.sh

## sources/test-tools/lcov/tests/xml2lcov/xml2lcov.sh

Purpose: Bash regression test for lcov's `xml2lcov` converter. It exercises successful conversion of a bundled Cobertura-style `coverage.xml`, usage/help behavior, expected failures for missing source/version data and bad command lines, lcov aggregation syntax validation, and optional Python coverage reporting.

Important APIs/functions: the script is command-line orchestration rather than a library. It consumes variables and helper functions from `../common.tst`, including `clean_cover`, `PYCOVER`, `XML2LCOV_TOOL`, `LCOV_TOOL`, `PY2LCOV_TOOL`, `GENHTML_TOOL`, `KEEP_GOING`, `CLEAN_ONLY`, `USE_GIT`, `IS_GIT`, `IS_P4`, `PARALLEL`, `PROFILE`, and coverage-related paths. It dynamically selects version and annotate scripts for git or Perforce.

Control flow: cleanup is first, then an early `CLEAN_ONLY` exit. The test establishes VCS-specific `VERSION`/`ANNOTATE` options, requires `PY2LCOV_SCRIPT` to be executable, runs positive xml2lcov conversions, runs negative conversions that must fail, captures `--help` output and greps for usage text, aggregates generated lcov info with `--ignore inconsistent`, and optionally emits lcov/genhtml coverage for the Python converter.

State and persistence: creates and deletes local `*.info`, `*.json`, `help.txt`, `*.pyc`, `*.dat`, `__pycache__`, and generated coverage folders/files. It does not modify repository configuration.

Dependencies/integration: depends on lcov test harness conventions, bundled `coverage.xml`, VCS helper scripts, Python coverage tooling, and lcov/genhtml binaries. Integration point is the lcov test suite, where exit status determines pass/fail.

Risks: heavy use of `eval` around tool/options variables can misbehave if variables contain unexpected shell metacharacters. Negative tests assume version lookup fails without source. The disabled keep-going block is untested drift risk. Aggregation knowingly tolerates inconsistent coverage input.

Test signals: explicit failure messages and exits on unexpected status; final `Tests passed`; lcov aggregation validates generated syntax.
