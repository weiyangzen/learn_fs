
# sources/security-integrity/ima-evm-utils/tests/functions.sh

## Purpose
`functions.sh` is the shared Bash test harness for ima-evm-utils. It provides automake-compatible pass/fail/skip accounting, wrappers for positive and negative tests, `evmctl` execution, xattr extraction/assertion, OpenSSL engine setup, SoftHSM setup/teardown, and optional UML-style test environment initialization/cleanup.

## Important APIs, Types, And Functions
Key functions include `expect_pass()`, `expect_fail()`, `expect_pass_if()`, `expect_fail_if()`, `_evmctl_run()`, `_extract_xattr()`, `_test_xattr()`, `_enable_gost_engine()`, `_report_exit_and_cleanup()`, `_softhsm_setup()`, `_softhsm_teardown()`, `_run_env()`, `_exit_env()`, `_init_env()`, and `_cleanup_env()`. Exit code constants match automake: `OK=0`, `FAIL=1`, `SKIP=77`, with `HARDFAIL=99`.

## Control Flow
Tests call `expect_pass` or `expect_fail`, which enforce non-nesting, filter by `TST_LIST`, record outcomes, and optionally exit early. `_evmctl_run()` executes `evmctl` with verbosity/engine settings, captures output to a temporary file, classifies hard command failures, and prints diagnostics depending on expected outcome and verbosity. Environment helpers set up mounts and shutdown behavior when running as PID 1 in a test VM.

## State And Persistence
Global counters and mode flags track test state. Temporary output files are deleted after each command. `WORKDIR`, SoftHSM config directories, mounted filesystems, and generated key/token state are cleaned by helper functions when tests cooperate.

## Dependencies And Integration Points
The harness depends on Bash, automake exit code conventions, `getfattr`, `xxd`, OpenSSL, optional GOST engine, SoftHSM, GnuTLS `p11tool`, and kernel filesystems for environment tests.

## Risks
The script uses global variables heavily, so tests must reset or avoid collisions. `_evmctl_run()` builds a command string and executes it unquoted through `$cmd`, which is convenient for option injection but sensitive to paths with spaces. VM cleanup can call `poweroff -f` when running in test environment mode.

## Test Signals
All userspace and kernel shell tests report through this harness; failures here affect every test's classification and diagnostics.
