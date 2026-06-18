# sources/test-tools/lcov/tests/llvm2lcov/llvm2lcov.sh

## Purpose

`llvm2lcov.sh` is a comprehensive integration test for converting LLVM `llvm-cov export` JSON into LCOV `.info` data. It validates line, function, branch, macro, exclude, checksum, help/error, genhtml, and version-specific MC/DC behavior.

## Important APIs, types, and functions

The script uses `clang++ -fprofile-instr-generate -fcoverage-mapping`, optional `-fcoverage-mcdc`, `llvm-profdata merge`, `llvm-cov export -format=text`, `LLVM2LCOV_TOOL`, `GENHTML_TOOL`, `LCOV_OPTS="--branch-coverage $PARALLEL $PROFILE"`, `--rc function_coverage=0`, `--branch`, `--mcdc`, `--exclude`, `--ignore empty`, and fixture-specific `grep` checks for `FNL`, `FNA`, `DA`, `BRDA`, `BRF`, `BRH`, `MCDC`, `MCF`, and `MCH`.

## Control flow

The script resolves `LCOV_HOME`, cleans artifacts, skips gracefully when Clang is unavailable or unusable, and enables MC/DC for Clang 18+. It builds and runs `main.cpp`, merges raw profiles, exports JSON, then exercises `llvm2lcov` in line-only, branch-only, MC/DC-only, and combined modes. It renders HTML from the combined output, reruns conversion with `--exclude '*/main.cpp'`, and checks that branch-empty warnings appear. It then validates exact function records, hit/miss line records, non-instrumented lines, branch expressions and totals, and LLVM-version-dependent MC/DC records. It finishes with help and bad-option checks and optional local coverage report generation.

## State and persistence behavior

Generated state includes `test`, `*.profraw`, `test.profdata`, `test.json`, several `.info` files, `exclude.log`, and `report`. Optional local coverage creates Perl and HTML coverage artifacts under the configured coverage database.

## Dependencies and integration points

It depends on Clang/LLVM tools, `llvm2lcov`, `genhtml`, Bash, the common harness, and source layout in `main.cpp`/`test.h`. It directly exercises the converter researched separately in `sources/test-tools/lcov/bin/llvm2lcov`.

## Risks and test signals

This is highly coupled to LLVM JSON and instrumentation behavior. It contains explicit branches for LLVM versions before 16, before/after 18, and 21+. Core signals include exact function/line/branch counts, macro-origin branch records, MC/DC schema-specific expectations, successful genhtml validation, and correct failures for unsupported options.
