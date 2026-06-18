# sources/test-tools/lcov/tests/lcov/initializer/initializer.sh

## Purpose

`initializer.sh` verifies LCOV's `initializer` filter for C++ initializer-list coverage records, while also filtering line and branch artifacts.

## Important APIs, types, and functions

It uses `common.tst`, `CXX`, `CC`, `GENINFO_TOOL`, `COVER`, `KEEP_GOING`, and `LOCAL_COVERAGE`. It compiles `initializer.cpp` with `--coverage -std=c++17`, captures with `geninfo`, applies `--demangle`, `--rc derive_function_end_line=0`, `--filter line,branch` and then `--filter line,branch,initializer`, and counts `DA:` lines.

## Control flow

The script cleans artifacts, skips old GCC versions lacking suitable C++/lambda-era support, skips if GCC is older than 8 for C++17 support, and requires `CXX`. It compiles and runs the program, captures unfiltered coverage into `initializer.info`, then captures filtered coverage into `filtered.info`. If the unfiltered file contains `DA:` records on initializer-list lines 8, 9, or 10, it asserts the filtered output has exactly three fewer `DA:` records.

## State and persistence behavior

Generated state includes the `initializer` executable, `.gcda`, `.gcno`, `.info`, `.log`, `.json`, and report artifacts, all removed in clean mode. The script uses `COUNT`, `COUNT2`, and `DIFF` to enforce expected filtering.

## Dependencies and integration points

It depends on C++17 compilation, GCC coverage output shape, `geninfo`, demangling support, and LCOV's source-line filters. It integrates with compiler-version gates to avoid false failures on unsupported toolchains.

## Risks and test signals

The line numbers in the grep are coupled to `initializer.cpp`. The test is robust to compilers that do not emit initializer-list line points by logging that no such points exist, but when points exist the exact three-line reduction is the key signal.
