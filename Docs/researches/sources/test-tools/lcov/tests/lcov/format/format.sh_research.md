# sources/test-tools/lcov/tests/lcov/format/format.sh

## Purpose

`format.sh` tests LCOV parsing and diagnostic behavior for malformed or suspicious `.info` data in `format.info`. It exercises error classification for negative counts, format errors, excessive counts, warning summaries, and `--keep-going` behavior.

## Important APIs, types, and functions

The script is procedural and uses `common.tst` variables plus `LCOV_OPTS="--branch $PARALLEL $PROFILE"`. It calls `lcov --summary`, `lcov -a`, `--ignore format,negative,excessive`, `--rc excessive_count_threshold=1000000`, and `--keep-going`. It inspects `PIPESTATUS[0]` after `tee`, `grep`s for `ERROR:` and `WARNING:` classes, checks warning type summary lines, and uses `diff` to compare sanitized outputs.

## Control flow

After cleanup and compiler/tool checks, it first expects `lcov --summary format.info` to fail with one `(negative)` error. It repeats with `--ignore negative`, expecting a `(format)` error. Then it adds the tracefile while ignoring format and negative errors, expects three warnings for each class and summary counts, and validates that the generated `out.info` is clean. It tests excessive-count handling twice: without `--keep-going`, the command must fail and not write output; with `--keep-going`, it must still fail but write an output identical to the clean result. Finally, with `--ignore excessive`, it expects warning-mode completion and multiple excessive warnings.

## State and persistence behavior

It removes gcov files, `.info` outputs, logs, JSON, and temporary artifacts at startup or in clean mode. It writes diagnostic logs such as `err1.log`, `warn.log`, `excessive.log`, `keepGoing.log`, and generated tracefiles. The script exits on first failure unless `KEEP_GOING` allows continued checks.

## Dependencies and integration points

The test depends on the fixture `format.info`, LCOV's parser and message-classification logic, Bash `PIPESTATUS`, and optional `CXX` availability even though it does not compile test C++ in this script. It integrates with LCOV's ignore-error policy and excessive-count threshold configuration.

## Risks and test signals

Expected warning counts are exact, so changes in parser recovery or diagnostic de-duplication can break the test. The important signals are failing where failure is expected, producing or suppressing `out2.info` according to `--keep-going`, and preserving identical sanitized output across equivalent runs.
