# sources/test-tools/fio/t/fiotestcommon.py

## Purpose
Provides shared success-policy dictionaries, safe file reading, and environment requirement probes for fio Python regression tests.

## Important APIs, Types, and Functions
`SUCCESS_DEFAULT`, `SUCCESS_LONG`, `SUCCESS_NONZERO`, and `SUCCESS_STDERR` describe expected return/stderr/timeout behavior. `get_file()` reads text using the preferred locale encoding. `Requirements` computes class-level booleans and exposes requirement callbacks such as `linux()`, `libaio()`, `io_uring()`, `zbd()`, `root()`, `zoned_nullb()`, `not_macos()`, `not_windows()`, `unittests()`, `cpucount4()`, and `nvmecdev()`.

## Control Flow
Constructing `Requirements(fio_root, args)` probes the host platform. On Linux it reads `config-host.h` for feature macros, checks `/proc/kallsyms` for `io_uring_setup`, tests effective UID, and optionally tries `modprobe null_blk` for zoned-nullb support. It also checks for a built unittest binary, CPU count, and an optional NVMe character device argument, then logs every requirement result.

## State and Persistence Behavior
Requirement results are class variables, so one probe establishes process-global state for subsequent callbacks. External side effects are limited to possible `modprobe null_blk` execution.

## Dependencies and Integration Points
Used by test scripts through requirement lists consumed by `run_fio_tests()`. It depends on fio build artifacts, Linux proc/sysfs conventions, Python platform APIs, and command execution.

## Risks
Missing `config-host.h` sets ZBD to true but leaves some other feature flags false, which can over-admit zoned tests in unusual trees. `/proc/kallsyms` visibility can be restricted, making io_uring probing conservative. Class-level state can become stale if multiple different fio roots or argument sets are probed in one interpreter.

## Test Signals
Tests should check requirement callbacks on Linux/non-Linux mocks, missing config handling, unittest path detection, CPU-count threshold, and `args.nvmecdev` propagation.
