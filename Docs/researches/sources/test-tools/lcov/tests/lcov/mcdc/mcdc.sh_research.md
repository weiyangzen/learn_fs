# sources/test-tools/lcov/tests/lcov/mcdc/mcdc.sh

## Purpose

`mcdc.sh` validates LCOV MC/DC capture and rendering across GCC and LLVM flows. It checks tool help/error paths, GCC `-fcondition-coverage` conversion through `geninfo`, LLVM JSON conversion through `llvm2lcov`, `genhtml --mcdc`, source exclusion, and MC/DC filtering behavior.

## Important APIs, types, and functions

It defines two helpers. `runClang()` builds with `clang++ -fprofile-instr-generate -fcoverage-mapping -fcoverage-mcdc`, runs `llvm-profdata`, exports JSON via `llvm-cov`, converts with `LLVM2LCOV_TOOL --branch --mcdc`, renders with `GENHTML_TOOL --branch --mcdc`, and verifies `--exclude '*/main.cpp'` leaves one source file. `runGcc()` builds with `g++ --coverage -fcondition-coverage`, runs the binary, captures with `GENINFO_TOOL --mcdc --branch`, renders with `genhtml`, and accepts extra geninfo filter arguments. The script also selects `GET_VERSION` from Git or P4 version scripts.

## Control flow

The script cleans prior artifacts, selects version-script integration, enables GCC MC/DC for GCC 14+ and LLVM MC/DC for Clang 14+, and performs `llvm2lcov --help` and bad-option checks. For GCC-capable compilers it runs several builds with different `SENS1`, `SENS2`, and `SIMPLE` flags, then checks whether `--filter mcdc` removes MC/DC only in the expected simple-condition case. For LLVM-capable compilers it runs three Clang builds covering the same sensitivity matrix. `STATUS` accumulates failures and controls final exit.

## State and persistence behavior

Generated state includes `*.profraw`, `*.profdata`, JSON files, `.info` files, genhtml report directories, GCC `.gcno/.gcda`, and test executables. Helper functions clean profile or gcov files between runs to avoid cross-test contamination.

## Dependencies and integration points

It depends on GCC/Clang version capabilities, `llvm-profdata`, `llvm-cov`, `llvm2lcov`, `geninfo`, `genhtml`, version scripts, and the common harness. It integrates the same C++ sources through two coverage ecosystems and compares LCOV's ability to represent/report MC/DC records.

## Risks and test signals

The test is highly version-sensitive. LLVM and GCC can change MC/DC schema, instrumentation, or option availability. Signals include successful report generation, expected include/exclude source counts, presence or absence of `MCDC` records under filters, and correct failure for unsupported `llvm2lcov` arguments.
