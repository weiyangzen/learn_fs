# sources/test-tools/lcov/tests/py2lcov/py2lcov.sh

## Purpose

`py2lcov.sh` is a broad integration test for converting Coverage.py data to LCOV. It validates direct database conversion, legacy XML conversion, function extraction, checksums, version/annotation scripts, exclusion, help and usage errors, environment-variable input, aggregation, and LCOV filtering behavior.

## Important APIs, types, and functions

The script uses `coverage` or `python3-coverage`, `PY2LCOV_TOOL`, `GENHTML_TOOL`, `LCOV_TOOL`, optional `PYCOVER`, version scripts (`gitversion` or `P4version.pm`), annotate scripts (`gitblame.pm` or `p4annotate.pm`), `--cmd`, `-i`, `--checksum`, `--no-function`, `--exclude`, `--keep-going`, `COVERAGE_FILE`, and LCOV filters `region` and `branch_region`.

## Control flow

It resolves `LCOV_HOME`, cleans artifacts, selects version/annotate integration based on Git/P4 availability, locates a coverage command, and runs `coverage run --branch ./test.py -v -v` into `functions.dat`. It converts directly to `functions.info`, verifies unhit lines and expected nested/local function records, and validates with genhtml. It emits XML from the same data, converts through legacy XML mode, and requires identical output. It tests checksums, combined genhtml with version/annotation data, `--no-function`, no-version behavior, source exclusion, help output, version-script error and keep-going fallback, missing-input and unsupported-argument errors, `COVERAGE_FILE` input discovery, LCOV aggregation of generated info files, and filtering of Python exclusion regions.

## State and persistence behavior

Generated state includes coverage databases (`functions.dat`), XML, many `.info` files, reports `rpt1`/`rpt2`, `my_cache`, `help.txt`, Python caches, and optional local coverage products. Clean mode removes these artifacts.

## Dependencies and integration points

It depends on Python 3, Coverage.py command-line behavior, `py2lcov`, LCOV/genhtml, source-control version/annotation scripts, and the Python fixtures. It integrates converter output with downstream LCOV aggregation and HTML validation.

## Risks and test signals

This test is sensitive to Coverage.py data format, source-control availability, and exact function line ranges in `test.py` and `localmodule.py`. Strong signals include direct-vs-XML identical output, expected nested function records, checksum-bearing DA records, correct exclusion and usage errors, environment-input equivalence, and region-filter count reductions.
