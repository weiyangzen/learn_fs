# sources/test-tools/lcov/tests/lcov/gcov-tool/path.sh

## Purpose

`path.sh` verifies `--gcov-tool` handling for both `lcov --capture` and direct `geninfo`, including default gcov, bare tool names, absolute wrapper paths, relative wrapper paths, and expected failures for nonexistent tools.

## Important APIs, types, and functions

It defines `TOOLS=( "$CC" "gcov" )` and `check_tools()` to validate prerequisites with `type -P`. It uses `CC`, `COVER`, `LCOV_TOOL`, `GENINFO_TOOL`, `KEEP_GOING`, `CLEAN_ONLY`, and `LOCAL_COVERAGE` from `common.tst`. The core loop iterates over two command forms: `$LCOV_TOOL --capture -d` and `$GENINFO_TOOL`.

## Control flow

The script cleans old compiler coverage data, verifies tools, builds `test.c` with `--coverage`, and runs the resulting binary. For each capture command form, it performs successful captures with no `--gcov-tool`, with `--gcov-tool gcov`, with an absolute path to `mygcov.sh`, and with `./mygcov.sh`. It then expects failure for a missing bare command, missing absolute path, and missing relative path. `status` accumulates failures while honoring `KEEP_GOING`.

## State and persistence behavior

It produces `test`, `.gcno`, `.gcda`, and `test.info`, then overwrites `test.info` across cases. No durable state beyond generated coverage files is intended.

## Dependencies and integration points

The test depends on GCC-compatible coverage files, `gcov`, the wrapper `mygcov.sh`, LCOV/geninfo execution of external tools, and Bash arrays/functions. It checks both LCOV's higher-level capture path and geninfo's lower-level capture path.

## Risks and test signals

The test is path-sensitive: running from another directory, missing execute bits, or unusual `PATH` behavior can affect results. The main signal is the matrix of success for valid gcov-tool forms and failure for invalid forms across both command frontends.
