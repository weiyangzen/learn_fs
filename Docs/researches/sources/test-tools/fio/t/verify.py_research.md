# sources/test-tools/fio/t/verify.py

## Purpose
`verify.py` is the broad fio verify-options regression suite. It exercises checksum methods, verify-only reads, header seed/sequence behavior, async verify, verify backlog, verify interval/offset, pattern verification, random/sequential workloads, and deliberate corruption detection.

## Important APIs, Types, and Functions
`VerifyTest` wraps straightforward fio invocations and logs failed stderr/stdout/output artifacts. `VerifyCSUMTest` creates a multi-phase fio job: layout, expected-success verify-only/read phases, a `mangle` random write phase that corrupts data, and expected-failure verify-only/read phases. Its `check_result()` expects six named jobs and verifies corruption failures report `errno.EILSEQ`, except for `verify=null`.

Helper functions mutate shared test dictionaries before calling `run_fio_tests()`: `verify_test()` runs the base matrix across data directions and checksums; `verify_test_csum()` configures corruption tests and expected success semantics; `verify_test_header()` builds a matrix for mode and sequence behavior; `verify_test_vpi()` covers `verify_pattern_interval`. `CSUM_LIST1` is the default small checksum set, while `CSUM_LIST2` is selected by `--complete`.

## Control Flow and State
`main()` creates a top-level artifact directory, resolves fio root and binary, checks requirements, maps placeholder engines to platform-specific async/sync engines, then loops through products of directions, checksum methods, mangle block sizes, header modes/sequences, and pattern interval parameters. Read-only workloads reuse artifact directories from earlier write workloads so data exists for verification.

## Dependencies and Integration Points
The script depends on fio's test framework, platform-specific engine names, JSON output, `errno.EILSEQ`, and artifact-directory naming conventions used to locate prior write data. Some tests require four CPUs and skip on macOS.

## Risks and Test Signals
The suite mutates global `TEST_LIST*` structures repeatedly, so stale options must be explicitly removed. It can be long-running, especially with `--complete`. Risks include platform-specific engine differences, flakiness from CPU affinity or macOS file behavior, and reliance on directory-name replacement. Strong test signals include named job validation, expected error numbers, skipped counts, and exhaustive matrix coverage.
